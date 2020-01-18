from pyof.v0x04.common.utils import unpack_message
from pyof.v0x04.common.header import Header, Type
from pyof.v0x04.common.flow_match import Match, OxmOfbMatchField, MatchType
import struct
from pyof.foundation.base import GenericType
from pypacker.layer12 import arp,lldp,ethernet
from pypacker.layer3 import ip, ip6, ipx
from helpers import Port

import pyof


class Packet_switch(object):
    
    def __init__(self, msg, temp_switch=None):

        self.source_no = temp_switch.number
        self.print_result = False
        self.mac_src = None
        self.mac_dst = None
        self.ip_src = None
        self.ip_dst = None
        self.of_type = None
        self.in_port = None
        self.out_port = None
        self.eth_type = None
        self.slice_no = None
        self.dpid = None
        self.type_to_function = {Type.OFPT_HELLO:self.type_hello, 
                                Type.OFPT_ERROR:self.type_error,
                                Type.OFPT_PACKET_IN:self.type_packetin, 
                                Type.OFPT_FEATURES_REPLY:self.type_features_reply,
                                Type.OFPT_ECHO_REPLY:self.type_echo_reply,
                                Type.OFPT_ECHO_REQUEST:self.type_echo_request,
                                Type.OFPT_MULTIPART_REPLY:self.type_multipart_reply}
        try:
            self.msg = unpack_message(msg)
            self.parse_message(temp_switch)
        except Exception as e:
            print('EXCEPTION from Switch: ' + str(e))
        if self.print_result:
            self.print_the_packet_result()
    
    
    
    def type_echo_reply(self,temp_switch):
        pass
    def type_echo_request(self,temp_switch):
        pass
    def type_multipart_reply(self,temp_switch):
        pass
    def type_hello(self,temp_switch):
        pass
    def type_error(self,temp_switch):
        pass
    def type_packetin(self,temp_switch):
        self.in_port = self.msg.in_port
        try:
            # print("Lenght of the packet is : {}".format(str(len(self.msg.data._value))))

            eth = ethernet.Ethernet(self.msg.data._value)
            self.eth_type = eth.type_t
            self.print_result = True 
            if self.eth_type == 'ETH_TYPE_IP6':
                # ATTR list
                # print("IPv6 with attr: {}".format(str(eth.__dict__.keys())))
                #(['_lazy_handler_data', '_body_bytes', '_body_changed', '_header_len', '_header_cached', '_header_changed', '_unpacked', '_dst', '_src', '_type'])

                # print("IPv6 packet's _src: {}".format(str(eth._src)))                                         # == Address in bytes hex
                # print("IPv6 packet's _unpacked: {}".format(str(eth._unpacked)))                               # == TRUE
                # print("IPv6 packet's _lazy_handler_data: {}".format(str(eth._lazy_handler_data)))             # class and bytes
                # print("IPv6 packet's _lazy_handler_data's DATA: {}".format(str(eth._lazy_handler_data[1])))   # A lot of HEX Bytes
                # print("The lazy handler data length is: {}".format(str(len(eth._lazy_handler_data[1]))))

                self.mac_src = eth.src_s
                self.mac_dst = eth.dst_s
                self.ip_dst = eth[ip6.IP6].dst_s
                self.ip_src = eth[ip6.IP6].src_s
                if self.in_port not in temp_switch.ports.keys():
                    temp_switch.ports[self.in_port] = Port(self.in_port)
                temp_switch.ports[self.in_port].update_mac_and_slice_no(self.mac_src)
            elif self.eth_type == 'ETH_TYPE_ARP':
                print("ARP with attr: {}".format(str(eth.__dict__.keys())))
                # self.mac_src = eth.src_s
            elif self.eth_type == 'ETH_TYPE_IP4':
                print("IP4 with attr: {}".format(str(eth.__dict__.keys())))
                # self.mac_src = eth.src_s
                # self.mac_dst = eth.dst_s
                # self.ip_dst = eth[ip.IP].dst_s
                # self.ip_src = eth[ip.IP].src_s   
                # self.slice_no = int(self.ip_src[0])
            else:
                print(self.eth_type)
        
            self.slice_no = temp_switch.ports[self.in_port].slice_no

        except Exception as e:
            print(e)
    
    def type_features_reply(self,temp_switch):
        #print("From dpid " + str(self.msg.datapath_id) + " : FEATURES_REPLY")
        self.dpid = self.msg.datapath_id
        temp_switch.dpid = self.dpid
        #self.print_result = True
        pass

    def parse_message(self,temp_switch):
        self.of_type = self.msg.header.message_type
        if self.of_type in self.type_to_function.keys():
            self.type_to_function[self.of_type](temp_switch)
        else:
            print("OPenflow Message Type " + str(self.of_type) + " Not in Dict")
            print(self.of_type)

    def print_the_packet_result(self):
        print("Packet from : Switch" + str(self.source_no))
        print("OF Packet Type : " + str(self.of_type))
        print("In Port : " + str(self.in_port))
        # print("Eth Packet type : " + str(self.eth_type))
        print("MAC source : " + str(self.mac_src))
        # print("MAC Dest : " + str(self.mac_dst))
        # print("IP Source : " + str(self.ip_src))
        # print("IP Dest : " + str(self.ip_dst) )
        print("Slice : " + str(self.slice_no) )
        # print("DPID : " + str(self.dpid))


class Packet_controller(object):
    
    def __init__(self, msg, controller_no):
        
        self.source_no = controller_no + 1
        self.print_result = False
        self.mac_src = None
        self.mac_dst = None
        self.ip_src = None
        self.ip_dst = None
        self.of_type = None
        self.in_port = None
        self.eth_type = None
        self.slice_no = None
        self.dpid = None
        self.type_to_function = {Type.OFPT_HELLO:self.type_hello, 
                                Type.OFPT_ERROR:self.type_error,
                                Type.OFPT_PACKET_OUT:self.type_packetout,
                                Type.OFPT_FEATURES_REQUEST:self.type_features_request,
                                Type.OFPT_PORT_STATUS:self.type_port_status,
                                Type.OFPT_ECHO_REPLY:self.type_echo_reply,
                                Type.OFPT_ECHO_REQUEST:self.type_echo_request,
                                Type.OFPT_MULTIPART_REQUEST:self.type_multipart_request,
                                Type.OFPT_FLOW_MOD:self.type_flow_mod}
        try:
            self.msg = unpack_message(msg)
            self.parse_message()
        except Exception as e:
            print("EXCEPTION from Controller" + str(e))
        if self.print_result:
            self.print_the_packet_result()
         
    def type_features_request(self):
        pass
    def type_port_status(self):
        pass
    def type_echo_reply(self):
        pass
    def type_echo_request(self):
        pass
    def type_multipart_request(self):
        pass
    def type_flow_mod(self):
        print("flooooooooow moooooooood")
        # 'header', 'cookie', 'cookie_mask', 'table_id', 'command', 'idle_timeout', 
        # 'hard_timeout', 'priority', #'buffer_id', 'out_port', 'out_group', 'flags', 
        # 'pad', 'match', 'instructions'
        # match: 'match_type', 'length', 'oxm_match_fields
        #print(str(self.msg.instructions[0].instruction_type)) InstructionType.OFPIT_APPLY_ACTIONS
        #instructions[0]: 'instruction_type', 'length', 'pad', 'actions
        #print("match_type: " + str(self.msg.match.match_type)) #MatchType.OFPMT_OXM
        print(str(self.msg.instructions[0].actions))#pyof.v0x04.common.action.ActionOutput object
        self.in_port = int.from_bytes(self.msg.match.get_field(OxmOfbMatchField.OFPXMT_OFB_IN_PORT),"big")
        #flow_match.OxmTLV objects: field, mask, value
        print("in_port: " + str(self.in_port))

        pass
    def type_hello(self):
        pass
    def type_error(self):
        pass                       
    def type_packetout(self):
         print("********packet out**********")
        # msg: (['header', 'buffer_id', 'in_port', 'actions_len', 'pad', 'actions', 'data'])
        # data: '_value', 'enum_ref'
        # actions:'_pyof_class' --> actionheader
        #print(str(self.msg.actions[0].port))
        self.out_port = int(str(self.msg.actions[0].port))
        #print("out_port: " + str(self.out_port))
            #'__module__', '__doc__', 'action_type', 'length', '_allowed_types', '__init__', 
            #'get_size', 'unpack', 'get_allowed_types'

        pass

    def parse_message(self):
        self.print_result = False
        self.of_type = self.msg.header.message_type
        if self.of_type in self.type_to_function.keys():
            self.type_to_function[self.of_type]()
        else:
            print("OPenflow Message Type " + str(self.of_type) + " Not in Dict")
            print(self.of_type)

    def print_the_packet_result(self):
        print("Packet from : Controller" + str(self.source_no))
        print("OF Packet Type : " + str(self.of_type))
        print("In Port : " + str(self.in_port))
        print("Eth Packet type : " + str(self.eth_type))
        print("MAC source : " + str(self.mac_src))
        print("MAC Dest : " + str(self.mac_dst))
        print("IP Source : " + str(self.ip_src))
        print("IP Dest : " + str(self.ip_dst) )
        print("Slice : " + str(self.slice_no) )
        print("DPID : " + str(self.dpid))

       

        
        