from pyof.v0x04.common.utils import unpack_message
from pyof.v0x04.common.header import Header, Type
from pyof.v0x04.common.flow_match import Match, OxmOfbMatchField, MatchType
import struct
from pyof.foundation.base import GenericType
from pypacker.layer12 import arp,lldp,ethernet
from pypacker.layer3 import ip, ip6, ipx
from helpers import Port

import pyof

FLOOD_PORT = 4294967291


class Packet_switch(object):
    
    def __init__(self, msg, forwarder):
        self.mac_addrlist = forwarder.mac_add
        temp_switch = forwarder.proxy_port_switch_dict[forwarder.s.getpeername()[1]]
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
        self.buffer_id = None
        self.ARP_src_mac = None     # recently added
        self.ARP_dst_mac = None     # recently added
        self.version = None #int
        self.type_to_function = {Type.OFPT_HELLO:self.type_hello, 
                                Type.OFPT_ERROR:self.type_error,
                                Type.OFPT_PACKET_IN:self.type_packetin, 
                                Type.OFPT_FEATURES_REPLY:self.type_features_reply,
                                Type.OFPT_ECHO_REPLY:self.type_echo_reply,
                                Type.OFPT_PORT_STATUS:self.type_port_status,
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
        '''
        print("*******multipart_reply*********")
        # header', 'multipart_type'(int), 'flags'(int), 'pad', 'body'(pyof.v0x04.common.port.Port )
        #print(str(self.msg.header))
        ports = []
        for port in self.msg.body:
            print("port n: hw_addr ",port.port_no,port.hw_addr)
            #name, config, state, curr, advertised, supported, peer, curr_speed, max_speed
            ports.append(port)
        '''
        pass
    def type_hello(self,temp_switch):
        #print("*******hello*********")
        self.version = int(str(self.msg.header.version))
        pass
    def type_error(self,temp_switch):
        pass
    def type_packetin(self,temp_switch):
        self.in_port = self.msg.in_port
        self.buffer_id = self.msg.buffer_id
        try:
            # print("Lenght of the packet is : {}".format(str(len(self.msg.data._value))))
            eth = ethernet.Ethernet(self.msg.data._value)
            self.eth_type = eth.type_t
            self.print_result = False 

            if self.eth_type == 'ETH_TYPE_IP6':
                # ATTR list
                # print("IPv6 with attr: {}".format(str(eth.__dict__.keys())))
                #(['_lazy_handler_data', '_body_bytes', '_body_changed', '_header_len', '_header_cached', '_header_changed', '_unpacked', '_dst', '_src', '_type'])

                ####### TO GET ATTR FROM PACKETINS #######
                # print("IPv6 packet's _src: {}".format(str(eth._src)))                                         # == Address in bytes hex
                # print("IPv6 packet's _unpacked: {}".format(str(eth._unpacked)))                               # == TRUE
                # print("IPv6 packet's _lazy_handler_data: {}".format(str(eth._lazy_handler_data)))             # class and bytes
                # print("IPv6 packet's _lazy_handler_data's DATA: {}".format(str(eth._lazy_handler_data[1])))      # A lot of HEX Bytes
                # print("The lazy handler data length is: {}".format(str(len(eth._lazy_handler_data[1]))))

                self.mac_src = eth.src_s
                self.mac_dst = eth.dst_s
                self.ip_dst = eth[ip6.IP6].dst_s
                self.ip_src = eth[ip6.IP6].src_s
                if self.mac_src not in self.mac_addrlist:
                    self.mac_addrlist.append(self.mac_src)
                pass
            elif self.eth_type == 'ETH_TYPE_ARP':
                # print("ARP with attr: {}".format(str(eth.__dict__.keys())))
                self.mac_src = eth.src_s
                self.mac_dst = eth.dst_s
                self.ip_dst = eth[arp.ARP].tpa_s
                self.ip_src = eth[arp.ARP].spa_s
                self.ARP_src_mac = eth[arp.ARP].sha_s
                self.ARP_dst_mac = eth[arp.ARP].tha_s
                self.slice_no = int(self.ip_src[0])
                self.print_result = False

                ## COOLER IMPLEMENTATION LATER
                if self.in_port not in temp_switch.ports.keys():
                    temp_switch.ports[self.in_port] = Port(self)
                if self.slice_no not in temp_switch.ports[self.in_port].list_of_slices:
                    temp_switch.ports[self.in_port].list_of_slices.append(self.slice_no)
                # print("SWITCH{}'s PORT{}'s SLICE LIST: {}".format(str(temp_switch.number),str(self.in_port),str(temp_switch.ports[self.in_port].list_of_slices)))

                pass
            elif self.eth_type == 'ETH_TYPE_IP4':
                # print("IP4 with attr: {}".format(str(eth.__dict__.keys())))
                self.mac_src = eth.src_s
                self.mac_dst = eth.dst_s
                self.ip_dst = eth[ip.IP].dst_s
                self.ip_src = eth[ip.IP].src_s  
                self.slice_no = int(self.ip_src[0])
                
                # if self.in_port not in temp_switch.ports.keys():
                #     temp_switch.ports[self.in_port] = Port(self.in_port)
                # temp_switch.ports[self.in_port].update_mac_and_slice_no(self.mac_src)
                pass
            elif self.eth_type == 'ETH_TYPE_IP':
                # print("WHO THE FUCK??? IP with attr: {} \n".format(str(eth.__dict__.keys())))
                pass
            else:
                print('This ETH_TYPE is not used: ' + str(self.eth_type))

            # self.slice_no = temp_switch.ports[self.in_port].slice_no

        except Exception as e:
            print('EXCEPTION ETH packet parsing: ' + str(e))
    
    def type_features_reply(self,temp_switch):
        #print("*****Features reply*****")
        #print("From dpid " + str(self.msg.datapath_id) + " : FEATURES_REPLY")
        
        #self.n_buffers=int(str(self.msg.n_buffers))
        #self.n_tables=int(str(self.msg.n_tables))
        #self.auxiliary_id=int(str(self.msg.auxiliary_id))
        #self.capabilities=int(str(self.msg.capabilities))
        #self.reserved=int(str(self.msg.reserved))
        
        #'header', 'datapath_id', 'n_buffers', 'n_tables', 'auxiliary_id', 'pad', 'capabilities', 'reserved'
        self.dpid = self.msg.datapath_id
        temp_switch.dpid = self.dpid
        #self.print_result = True
        pass

    def type_port_status(self, temp_switch):
        #print("*****port_status*****")
        '''
        reason = self.msg.reason
        port_no = int(str(self.msg.desc.port_no))
        hw_addr = str(self.msg.desc.hw_addr)

        #header', 'reason', 'pad', 'desc'->(port)
        #desc: port_no, pad, hw_addr, pad2, name(str), config, state, curr, advertised, supported, peer, curr_speed, max_speed
        
        name = str(self.msg.desc.name)) #name of the switch e.g. s3
        config = int(self.msg.desc.config) #enum_ref --> common.port.PortConfig
        state = int(self.msg.desc.state) #enum_ref --> common.port.PortSate
        curr = int(self.msg.desc.curr) #enum_ref --> common.port.PortFeatures
        advertised = int(self.msg.desc.advertised) #enum_ref --> common.port.PortFeatures
        supported = int(self.msg.desc.supported) #enum_ref --> common.port.PortFeatures
        peer = int(self.msg.desc.peer) #enum_ref --> common.port.PortFeatures
        curr_speed = int(self.msg.desc.curr_speed)
        max_speed = int(self.msg.desc.max_speed)
        '''
        pass

    def parse_message(self,temp_switch):
        self.of_type = self.msg.header.message_type
        if self.of_type in self.type_to_function.keys():
            self.type_to_function[self.of_type](temp_switch)
        else:
            print("OPenflow Message Type " + str(self.of_type) + " Not in Dict")

    def print_the_packet_result(self):
        print("Packet from : Switch" + str(self.source_no))
        print("OF Packet Type : " + str(self.of_type))
        print("In Port : " + str(self.in_port))
        print("Eth Packet type : " + str(self.eth_type))
        print("MAC source : " + str(self.mac_src))
        print("MAC Dest : " + str(self.mac_dst))
        print("IP Source : " + str(self.ip_src))
        print("IP Dest : " + str(self.ip_dst) )
        print("Slice : " + str(self.slice_no) )
        # print("DPID : " + str(self.dpid))
        print("ARP Source mac : " + str(self.ARP_src_mac))
        print("ARP Destination mac : " + str(self.ARP_dst_mac))


class Packet_controller(object):
    
    def __init__(self, msg, controller_no):
        
        self.source_no = controller_no + 1
        self.print_result = False
        self.mac_src = None
        self.mac_dst = None
        self.buffer_id = None
        self.ip_src = None
        self.ip_dst = None
        self.of_type = None
        self.in_port = None #int
        self.out_port = None #int
        self.eth_type = None
        self.slice_no = None
        self.dpid = None
        self.version = None  #int 
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
        # print("*************flow mod**************")
        # msg:  'header', 'cookie', 'cookie_mask', 'table_id', 'command', 'idle_timeout', 
        #       'hard_timeout', 'priority', #'buffer_id', 'out_port', 'out_group', 'flags', 
        #       'pad', 'match', 'instructions'
        # match: 'match_type', 'length', 'oxm_match_fields
        
        # instructions[0]: 'instruction_type', 'length', 'pad', 'actions
        instruction_len = len(self.msg.instructions)
        
        if instruction_len == 1:
            action_len = len(self.msg.instructions[0].actions)
            
            if action_len == 1:
                self.out_port = int(str(self.msg.instructions[0].actions[0].port))
                # print("flow mod out port (actions[0]): " + str(self.out_port))
            else:
                print("************flow mod actions length: " + str(action_len))
                pass

        else:
            print("************flow mod instructions length  = " + str(instruction_len))
            pass

        self.in_port = int.from_bytes(self.msg.match.get_field(OxmOfbMatchField.OFPXMT_OFB_IN_PORT),"big")


        pass
    def type_hello(self):
        self.version = int(str(self.msg.header.version))
        #header: 'version', 'message_type', 'length', 'xid'
        #msg.elements: []
        pass
    def type_error(self):
        pass                       
    def type_packetout(self):
        #print("********packet out**********")
        # msg: (['header', 'buffer_id', 'in_port', 'actions_len', 'pad', 'actions', 'data'])
        # data: '_value', 'enum_ref'
        # action[0]:'length', 'port', 'action_type', 'max_length', 'pad'

        action_len = len(self.msg.actions)
        self.buffer_id = self.msg.buffer_id
        if action_len == 1:
            self.out_port = int(str(self.msg.actions[0].port))
            if self.out_port == FLOOD_PORT:
                # print("PACKET_OUT port (actions[0]): FLOOD")
                pass
            else:
                print("*********PACKET_OUT port (actions[0]): " + str(self.out_port))
        else:
            print("**********PACKET_OUT actions length: " + str(action_len))
            pass
        

        ''' parsing data'''

        '''
        try:
            # print("Lenght of the packet is : {}".format(str(len(self.msg.data._value))))
            if len(self.msg.data._value) > 0:
                
                print("packetout msg data length: " + str(len(self.msg.data._value)))
                print(self.msg.data._value)
                print("packetout msg type: " + str(self.eth_type))
                eth = ethernet.Ethernet(self.msg.data._value)
                
                self.eth_type = eth.type_t
                self.print_result = False 
                

                if self.eth_type == 'ETH_TYPE_IP6':
                    print("****packet out IPv6****")
                    # ATTR list
                    # print("IPv6 with attr: {}".format(str(eth.__dict__.keys())))
                    #(['_lazy_handler_data', '_body_bytes', '_body_changed', '_header_len', '_header_cached', '_header_changed', '_unpacked', '_dst', '_src', '_type'])

                    ####### TO GET ATTR FROM PACKETINS #######
                    # print("IPv6 packet's _src: {}".format(str(eth._src)))                                         # == Address in bytes hex
                    # print("IPv6 packet's _unpacked: {}".format(str(eth._unpacked)))                               # == TRUE
                    # print("IPv6 packet's _lazy_handler_data: {}".format(str(eth._lazy_handler_data)))             # class and bytes
                    # print("IPv6 packet's _lazy_handler_data's DATA: {}".format(str(eth._lazy_handler_data[1])))      # A lot of HEX Bytes
                    # print("The lazy handler data length is: {}".format(str(len(eth._lazy_handler_data[1]))))

                    self.mac_src = eth.src_s
                    self.mac_dst = eth.dst_s
                    self.ip_dst = eth[ip6.IP6].dst_s
                    self.ip_src = eth[ip6.IP6].src_s
                    pass
                elif self.eth_type == 'ETH_TYPE_ARP':
                    print("****packet out ARP****")
                    print("ARP with attr: {}".format(str(eth.__dict__.keys())))
                    self.mac_src = eth.src_s
                    self.mac_dst = eth.dst_s
                    self.ip_dst = eth[arp.ARP].tpa_s
                    self.ip_src = eth[arp.ARP].spa_s
                    self.ARP_src_mac = eth[arp.ARP].sha_s
                    self.ARP_dst_mac = eth[arp.ARP].tha_s
                    self.slice_no = int(self.ip_src[0])
                    self.print_result = True

                    ## COOLER IMPLEMENTATION LATER
                    if self.in_port not in temp_switch.ports.keys():
                        temp_switch.ports[self.in_port] = Port(self)
                    if self.slice_no not in temp_switch.ports[self.in_port].list_of_slices:
                        temp_switch.ports[self.in_port].list_of_slices.append(self.slice_no)
                    print("SWITCH{}'s PORT{}'s SLICE LIST: {}".format(str(temp_switch.number),str(self.in_port),str(temp_switch.ports[self.in_port].list_of_slices)))

                    pass
                elif self.eth_type == 'ETH_TYPE_IP4':
                    print("****packet out IPv4****")
                    print("IP4 with attr: {}".format(str(eth.__dict__.keys())))
                    self.mac_src = eth.src_s
                    self.mac_dst = eth.dst_s
                    self.ip_dst = eth[ip.IP].dst_s
                    self.ip_src = eth[ip.IP].src_s  
                    try:
                        self.slice_no = int(self.ip_src[0])
                    except Exception as e:
                        print("Exception trying to to get the slice from ipv4: " + str(e))
                    # if self.in_port not in temp_switch.ports.keys():
                    #     temp_switch.ports[self.in_port] = Port(self.in_port)
                    # temp_switch.ports[self.in_port].update_mac_and_slice_no(self.mac_src)
                    pass
                elif self.eth_type == 'ETH_TYPE_IP':
                    print("****packet out IP****")
                    # print("WHO THE FUCK??? IP with attr: {} \n".format(str(eth.__dict__.keys())))
                    pass
                else:
                    print('This ETH_TYPE is not used: ' + str(self.eth_type))

                # self.slice_no = temp_switch.ports[self.in_port].slice_no
            else:
                print("***packet out msg data length 0")
        except Exception as e:
                print('EXCEPTION ETH packet parsing: ' + str(e))
        '''

    def parse_message(self):
        self.print_result = False
        self.of_type = self.msg.header.message_type
        if self.of_type in self.type_to_function.keys():
            self.type_to_function[self.of_type]()
        else:
            print("OPenflow Message Type " + str(self.of_type) + " Not in Dict")
            pass

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

       

        
        