from pyof.v0x04.common.utils import unpack_message
from pyof.v0x04.common.header import Header, Type
from pyof.v0x04.common.flow_match import Match, OxmOfbMatchField, MatchType
import struct
from pyof.foundation.base import GenericType
from pypacker.layer12 import arp,lldp,ethernet
from pypacker.layer3 import ip, ip6, ipx

import pyof
from ryu.lib.packet import packet
import array


class Hyper_packet(object):
    
    def __init__(self, msg, source):

        # self.print_result = False
        # self.mac_src = None
        # self.mac_dst = None
        # self.ip_src = None
        # self.ip_dst = None
        # self.of_type = None
        # self.in_port = None
        # self.eth_type = None
        # self.slice = None
        # self.type_to_function = {Type.OFPT_HELLO:self.type_hello, 
        #                         Type.OFPT_ERROR:self.type_error,
        #                         Type.OFPT_PACKET_IN:self.type_packetin, 
        #                         Type.OFPT_PACKET_OUT:self.type_packetout,
        #                         Type.OFPT_FEATURES_REPLY:self.type_features_reply,
        #                         Type.OFPT_FEATURES_REQUEST:self.type_features_request,
        #                         Type.OFPT_PORT_STATUS:self.type_port_status,
        #                         Type.OFPT_ECHO_REPLY:self.type_echo_reply,
        #                         Type.OFPT_ECHO_REQUEST:self.type_echo_request,
        #                         Type.OFPT_MULTIPART_REQUEST:self.type_multipart_request,
        #                         Type.OFPT_MULTIPART_REPLY:self.type_multipart_reply}
        self.source = source
        # try:
            # self.msg = unpack_message(msg)
            # self.print_message_type_and_source()
            # self.parse_message()

        pkt = packet.Packet(array.array('B', msg))
        for p in pkt.protocols:
            print(p)
        # # print("From {} : {}".format(self.source,str(self.msg.header.message_type)))

        # except:
        #     print("Error with Unpacking")
        # if self.print_result:
            # self.print_the_packet_result()
         







    # def type_features_request(self):
    #     pass
    # def type_port_status(self):
    #     pass
    # def type_echo_reply(self):
    #     pass
    # def type_echo_request(self):
    #     pass
    # def type_multipart_reply(self):
    #     pass
    # def type_multipart_request(self):
    #     pass

    # def type_hello(self):
    #     #print("From " + self.source + ": OFPT_HELLO")
    #     pass

    # def type_error(self):
    #     #print("From {}: OFPT_ERROR of type {}".format(self.source,))
    #     pass

    # def type_packetin(self):
    #     self.in_port = self.msg.in_port
    #     try:
    #         eth = ethernet.Ethernet(self.msg.data._value)
    #         self.eth_type = eth.type_t
    #         if self.eth_type != 'ETH_TYPE_IP6':
    #             # self.print_result = True 
    #             if eth.type_t != 'ETH_TYPE_ARP':
    #                 self.mac_src = eth.src_s
    #                 self.mac_dst = eth.dst_s
    #                 self.ip_dst = eth[ip.IP].dst_s
    #                 self.ip_src = eth[ip.IP].src_s   
    #                 self.slice = self.ip_src[0]
    #             else:
    #                 self.mac_src = eth.src_s 
                                   
    #     except:
    #         print("1 failed")
    
             
    # def type_packetout(self):
    #     # print("From " + self.source + ': PACKET_OUT')  
    #     pass

    # def type_features_reply(self):
    #     #print("From " + self.source + ': ' str(msg.header.message_type))
    #     #print("From dpid " + str(self.msg.datapath_id) + " : FEATURES_REPLY")
    #     pass

    # def print_message_type_and_source(self):
    #     print("From {} : {}".format(self.source,str(self.msg.header.message_type)))

    # def parse_message(self):
    #     self.of_type = self.msg.header.message_type
    #     if self.of_type in self.type_to_function.keys():
    #         self.type_to_function[self.of_type]()
    #     else:
    #         print("OPenflow Message Type " + str(self.of_type) + " Not in Dict")
    #         print(self.of_type)

    # def print_the_packet_result(self):
    #     print("Packet from : " + self.source)
    #     print("OF Packet Type : " + str(self.of_type))
    #     print("In Port : " + str(self.in_port))
    #     print("Eth Packet type : " + str(self.eth_type))
    #     print("MAC source : " + str(self.mac_src))
    #     print("MAC Dest : " + str(self.mac_dst))
    #     print("IP Source : " + str(self.ip_src))
    #     print("IP Dest : " + str(self.ip_dst) )
    #     print("Slice : " + str(self.slice) )

       

        
        