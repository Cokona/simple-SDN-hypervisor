from pyof.v0x04.common.utils import unpack_message
from pyof.v0x04.common.header import Header, Type
import pyof

def parse_message(msg):
    #try:
    #if binary_packet[0] == 4:
        try:
            source = "HEY"
            msg = unpack_message(msg)
            if msg.header.message_type is Type.OFPT_HELLO:
                print("From " + source + ": OFPT_HELLO")
                pass
            elif str(msg.header.message_type) == 'Type.OFPT_ERROR':
                print("From " + source + ': OFPT_ERROR')
                pass
            elif str(msg.header.message_type) == 'Type.OFPT_PACKET_IN':
                print("From " + source + ': PACKET_IN')
                print(str(msg.reason))
                pass
            elif str(msg.header.message_type) == 'Type.OFPT_PACKET_OUT':
                print("From " + source + ': PACKET_OUT')
                #print(str(msg.reason))
                pass
            else:
                print("From " + source +  " : " + str(msg.header.message_type))          
        except:
            print("Error with Unpacking")
    # else:
    #     print("Not an OpenFlow Packet")