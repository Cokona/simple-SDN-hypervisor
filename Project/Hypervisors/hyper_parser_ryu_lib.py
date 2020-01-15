import struct
import pyof
from pyof.v0x04.common.utils import unpack_message
from pyof.v0x04.common.header import Header, Type
from pyof.v0x04.common.flow_match import Match, OxmOfbMatchField, MatchType

from pyof.foundation.base import GenericType
from pypacker.layer12 import arp,lldp,ethernet
from pypacker.layer3 import ip, ip6, ipx

from ryu.lib.packet import packet, openflow

class Hyper_packet(object):
    
    def __init__(self, data, source):

        self.print_result = False
        self.mac_src = None
        self.mac_dst = None
        self.ip_src = None
        self.ip_dst = None
        self.of_type = None
        self.in_port = None
        self.eth_type = None
        self.slice = None
        self.dpid = None
        self.source = source
        
        print("NEW MESSAGE")
        # print(msg)
        try:
            msg = openflow.openflow.parser(data)
        
            try:
                # msg_type_macro = msg[0].msg.msg_type       # This is a number that corresponds to the macro
                                                            # We should create a dict to crosscheck
                msg_type_string = type(msg[0].msg)             # class 'ryu.ofproto.ofproto_v1_3_parser.OFPPacketIn'
                if "class 'ryu.ofproto.ofproto_v1_3_parser.OFPPacketIn'":

                    pypacker_message = unpack_message(data)
                    print("--------UNFACKINGPARSEABLE, the actual msg type is {}".format(str(pypacker_message.header.message_type)))
                else: 
                    print(" * The string msg_type is {} and it has these attr: \n{}".format(msg_type_string, msg[0].msg.__dict__.keys()))
            except Exception as e:
                print(e)
                # print(" * The msg does not have a type? So maybe parsing error")

            try:
                msg_data = packet.Packet(msg[0].msg.data)
                print("  ** The message data is parsed as {}, and has the attributes: {}".format(str(msg_data),msg_data.__dict__.keys() ))

            except:
                msg_data = None
                print("Message has no msg.data")

        except:
            print("*Error with Unpacking the data with openflow.parser")
        
        if self.print_result:
            self.print_the_packet_result()
         

    def print_message_type_and_source(self):
        print("From {} : {}".format(self.source,str(self.msg.header.message_type)))

    def print_the_packet_result(self):
        print("Packet from : " + self.source)
        print("OF Packet Type : " + str(self.of_type))
        print("In Port : " + str(self.in_port))
        print("Eth Packet type : " + str(self.eth_type))
        print("MAC source : " + str(self.mac_src))
        print("MAC Dest : " + str(self.mac_dst))
        print("IP Source : " + str(self.ip_src))
        print("IP Dest : " + str(self.ip_dst) )
        print("Slice : " + str(self.slice) )
        print("DPID : " + str(self.dpid))

    

    # def type_packetin(self):
    #     self.in_port = self.msg.in_port
    #     try:
    #         eth = ethernet.Ethernet(self.msg.data._value)
    #         self.eth_type = eth.type_t
    #         if self.eth_type != 'ETH_TYPE_IP6':
    #             self.print_result = True 
    #             if eth.type_t != 'ETH_TYPE_ARP':
    #                 self.mac_src = eth.src_s
    #                 self.mac_dst = eth.dst_s
    #                 self.ip_dst = eth[ip.IP].dst_s
    #                 self.ip_src = eth[ip.IP].src_s   
    #                 self.slice = int(self.ip_src[0])
    #             else:
    #                 self.mac_src = eth.src_s 
                                   
    #     except:
    #         print("1 failed")
    
             
    # def type_packetout(self):
    #     # print("From " + self.source + ': PACKET_OUT')  
    #     pass


        
        