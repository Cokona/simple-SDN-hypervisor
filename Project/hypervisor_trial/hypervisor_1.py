from pyof.v0x04.common.utils import unpack_message
import socket, struct, fcntl

SIOCSIFADDR = 0X8916
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def setIPAddr(iface, ip):
    bin_ip = socket.inet_aton(ip)
    ifreq = struct.pack('16sH2s4s8s', iface, socket.AF_INET, '\x00'*2, bin_ip, '\x00'*8)
    fcntl.ioctl(sock, SIOCSIFADDR, ifreq)
setIPAddr('em1', '192.168.0.1')

'''
SIOCSIFADDR = 0X8916
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def setIPAddr(iface, ip):
    bin_ip = socket.inet_aton(ip)
    ifreq = struct.pack('16sH2s4s8s', iface, socket.AF_INET, '\x00'*2, bin_ip, '\x00'*8)
    fcntl.ioctl(sock, SIOCSIFADDR, ifreq)
setIPAddr('em1', '192.168.0.1')'''



# to parse a msg
binary_msg = b"\x01\x05\x00\x08\x14\xad'\x8d" # reveive msg from socket
msg = unpack_message(binary_msg)
print(msg.header.message_type)
'''
if type=='Type.OFPT_HELLO':
    #rewrite, add vlan_id
    #send msg to dst
elif type=='Type.OFPT_FEATURES_REQUEST':
    #add vlan_id
    #send msg to dst
elif type=='Type.OFPT_FEATURES_REPLY': 
    #rewrite switch ports
elif type=='Type.FLOW_MOD':
    increment the count for flow entries allocated to this controller in this switch
    if exeeded limit, send table full error message
'''