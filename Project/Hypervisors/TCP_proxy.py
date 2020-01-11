#!/usr/bin/python
# This is a simple port-forward / proxy, written using only the default python
# library. If you want to make a suggestion or fix something you can contact-me
# at voorloop_at_gmail.com
# Distributed over IDC(I Don't Care) license
import socket
import select
import time
import sys
from pyof.v0x04.common.utils import unpack_message
from pyof.v0x04.common.header import Header, Type
import pyof

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 1024
delay = 0.0001
forward_to = ('127.0.0.1', 6633)

def print_packet(binary_packet, source):
    try:
        #if binary_packet[0] == 4:
            #try:
        msg = unpack_message(binary_packet)
        
        if msg.header.message_type is Type.OFPT_HELLO:
            print("From " + source + ": OFPT_HELLO")
            # header(version, message_type, length, xid), elements(_pyof_class)
            pass
        elif msg.header.message_type is Type.OFPT_ERROR:
            print("From " + source + ': OFPT_ERROR')
            pass
        elif msg.header.message_type is Type.OFPT_PACKET_IN:
            print("From in_port no " + str(msg.in_port) + ': PACKET_IN')
           
            # header, buffer_id, in_port, actions_len, pad, actions, data
            #print(str(msg.header.__dict__.keys()))
            pass
        elif msg.header.message_type is Type.OFPT_PACKET_OUT:
            print("From " + source + ': PACKET_OUT')
            #print(str(msg.reason))
            #header, buffer_id, total_len, reason, table_id, cookie, match, pad, data
            pass
        elif msg.header.message_type is Type.OFPT_FEATURES_REPLY:
            print("From dpip " + str(msg.datapath_id) + ': Features_REPLY')
            #print(str(msg.reason))
            #header, buffer_id, total_len, reason, table_id, cookie, match, pad, data
            pass
        else:
            print("From " + source +  " : " + str(msg.header.message_type))          
    except:
        print("Error with Unpacking")
    # else:
    #     print("Not an OpenFlow Packet")


class Forward:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception as e:
            print(e)
            return False

class TheServer:
    input_list = []
    channel = {}

    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)

    def main_loop(self):
        self.input_list.append(self.server)
        while 1:
            time.sleep(delay)
            ss = select.select
            inputready, outputready, exceptready = ss(self.input_list, [], [])
            for self.s in inputready:
                if self.s == self.server:
                    self.on_accept()
                    break

                self.data = self.s.recv(buffer_size)
                if len(self.data) == 0:
                    self.on_close()
                    break
                else:
                    self.on_recv()

    def on_accept(self):
        forward = Forward().start(forward_to[0], forward_to[1])
        clientsock, clientaddr = self.server.accept()
        if forward:
            print(str(clientaddr) + " has connected")
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print("Can't establish connection with remote server.")
            print("Closing connection with client side" + str(clientaddr))
            clientsock.close()

    def on_close(self):
        print(str(self.s.getpeername()) + " has disconnected")
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        out = self.channel[self.s]
        # close the connection with client
        self.channel[out].close()  # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]

    def on_recv(self):
        data = self.data
        # here we can parse and/or modify the data before send forward
        print_packet(data, 'HEY')
        self.channel[self.s].send(data)

if __name__ == '__main__':
        server = TheServer('127.0.0.1', 65432)
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print("Ctrl C - Stopping server")
            sys.exit(1)