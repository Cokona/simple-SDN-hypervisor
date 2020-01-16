from pyof.v0x04.common.utils import unpack_message
from pyof.v0x04.common.header import Header, Type
from pyof.v0x04.common.flow_match import Match, OxmOfbMatchField, MatchType
import struct
from pyof.foundation.base import GenericType
from pypacker.layer12 import arp,lldp,ethernet
from pypacker.layer3 import ip, ip6, ipx

class Hyper_handler():
    def __init__(self,node_list, packet):
        self.type_to_function = {Type.OFPT_HELLO:self.handle_hello, 
                                Type.OFPT_ERROR:self.handle_error,
                                Type.OFPT_PACKET_IN:self.handle_packetin, 
                                Type.OFPT_PACKET_OUT:self.handle_packetout,
                                Type.OFPT_FEATURES_REPLY:self.handle_features_reply,
                                Type.OFPT_FEATURES_REQUEST:self.handle_features_request,
                                Type.OFPT_PORT_STATUS:self.handle_port_status,
                                Type.OFPT_ECHO_REPLY:self.handle_echo_reply,
                                Type.OFPT_ECHO_REQUEST:self.handle_echo_request,
                                Type.OFPT_MULTIPART_REQUEST:self.handle_multipart_request,
                                Type.OFPT_MULTIPART_REPLY:self.handle_multipart_reply}
        self.packet_type = packet.of_type
        if self.packet_type in self.type_to_function.keys():
            pass