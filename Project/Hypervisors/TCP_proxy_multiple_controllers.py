#!/usr/bin/python
# This is a simple port-forward / proxy, written using only the default python

import socket
import select
import time
import sys

import pyof
from pyof.v0x04.common.utils import unpack_message
from hyper_parser import Hyper_packet


# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 1024
delay = 0.0001

controller_address = ('127.0.0.1', 6633)
controller2_address = ('127.0.0.1', 6644)
hypervisor_address = ('127.0.0.1', 65432)

class Forward:
    '''
    Creates and returns socket connection to a controller
    '''
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self, host, port):
        try:
            # Create connection to the controller
            self.forward.connect((host, port))
            return self.forward
        except Exception as e:
            print(e)
            return False


class TheServer:
    input_list = []
    channel = {}
    channel2 = {}
    controller_sockets = []
    controller2_sockets = []
    switch_sockets = []
    
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)     # !NOTE Reconsider 200

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
        forward = Forward().start(controller_address[0], controller_address[1])
        forward2 = Forward().start(controller2_address[0], controller2_address[1])
        self.controller_sockets.append(forward)
        self.controller2_sockets.append(forward2)
        clientsock, clientaddr = self.server.accept()
        self.switch_sockets.append(clientsock)
        if forward or forward2:
            try:
                print(str(clientaddr) + " has connected")
                self.input_list.append(clientsock)
                self.input_list.append(forward)
                self.input_list.append(forward2)
                self.channel[clientsock] = forward
                self.channel[forward] = clientsock
                self.channel2[clientsock] = forward2
                self.channel2[forward2] = clientsock
            except:
                print("One of the two controller connections could not be set")
        else:
            print("Can't establish connection with remote server.")
            print("Closing connection with client side" + str(clientaddr))
            clientsock.close()

    def on_close(self):
        print(str(self.s.getpeername()) + " has disconnected")
        #remove objects from input_list
        self.input_list.remove(self.s)
        self.input_list.remove(self.channel[self.s])
        self.input_list.remove(self.channel2[self.s])
        out = self.channel[self.s]
        out2 = self.channel2[self.s]
        # close the connection with client
        self.channel[out].close()       # equivalent to do self.s.close()
        # close the connection with remote server
        self.channel[self.s].close()
        self.channel2[self.s].close()
        # delete both objects from channel dict
        del self.channel[out]
        del self.channel[self.s]
        del self.channel2[out2]
        del self.channel2[self.s]

    def on_recv(self):
        data = self.data
        # here we can parse and/or modify the data before send forward
        if self.s in self.controller_sockets:
            source = "Controller1"
            packet_info = Hyper_packet(data, source)
            self.channel[self.s].send(data)
        elif self.s in self.controller2_sockets:
            source = "Controller2"
            packet_info = Hyper_packet(data, source)
            self.channel2[self.s].send(data)
        elif self.s in self.switch_sockets:
            source = "Switch"
            packet_info = Hyper_packet(data, source)
            slice_no = packet_info.slice
            if slice_no is '1':
                self.channel[self.s].send(data)
                print('Forwarded to just Controller1')
            elif slice_no is '2':
                self.channel2[self.s].send(data)
                print('Forwarded to just Controller2')
            else:
                self.channel[self.s].send(data)
                self.channel2[self.s].send(data)
                print('Forwarded to BOTH Controllers')

        else:
            source = "--WHAT SOURCE--"

        # packet_info = Hyper_packet(data, source)
        # slice_no = packet_info.slice
        # if slice_no:
        #     print("Slice No is : " + str(slice_no))
       

if __name__ == '__main__':
        server = TheServer(hypervisor_address[0],hypervisor_address[1])
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print("Ctrl C - Stopping server")
            sys.exit(1)