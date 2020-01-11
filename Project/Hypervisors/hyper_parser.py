from pyof.v0x04.common.utils import unpack_message
from pyof.v0x04.common.header import Header, Type
import pyof



class Hyper_packet(object):
    
    def __init__(self, msg, source):
        self.type_to_function = {Type.OFPT_HELLO:self.type_hello, 
                                Type.OFPT_ERROR:self.type_error,
                                Type.OFPT_PACKET_IN:self.type_packetin, 
                                Type.OFPT_PACKET_OUT:self.type_packetout,
                                Type.OFPT_FEATURES_REPLY:self.type_features_reply}
        self.source = source
        try:
            self.msg = unpack_message(msg)
            self.parse_message()
        except:
            print("Error with Unpacking")
         
        

    def type_hello(self):
        print("From " + self.source + ": OFPT_HELLO")
        pass

    def type_error(self):
        print("From {}: OFPT_ERROR".format(self.source))
        pass

    def type_packetin(self):
        print("From {} in port no {}: PACKET IN".format(self.source, str(self.msg.in_port)))
        print(str(self.msg.reason))
        pass

    def type_packetout(self):
        print("From " + self.source + ': PACKET_OUT')  
        pass

    def type_features_reply(self):
        print("From " + self.source + ': OFPT_FEATURES_REPLY')
        print("From dpid " + str(self.msg.datapath_id) + " : FEATURES_REPLY")
        pass


    
    def parse_message(self):
        msg_type = self.msg.header.message_type
        if msg_type in self.type_to_function.keys():
            self.type_to_function[msg_type]()
        else:
            print(msg_type)

            
        