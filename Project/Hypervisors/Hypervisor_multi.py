#!/usr/bin/python
# This is a simple port-forward / proxy, written using only the default python

import socket
import select
import time
import sys
from helpers import Switch, Slice
import pyof
from pyof.v0x04.common.utils import unpack_message
from hyper_parser_kimon import Hyper_packet


# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 1024
delay = 0.0001
number_of_controllers = int(sys.argv[1])
controller_addresses = []

for i in range(number_of_controllers):
    controller_addresses.append(('127.0.0.1', 6633 + i))
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
    switch_sockets = []
    controller_sockets = []
    channels = []
    nodes = []
    switches = []
    port_switch_dict = {}
    for i in range(number_of_controllers):
        channels.append({})
        controller_sockets.append([])
    
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
        forwarders = []
        for i in range(number_of_controllers):
            forwarders.append(Forward().start(controller_addresses[i][0], controller_addresses[i][1]))
            self.controller_sockets[i].append(forwarders[i])
        clientsock, clientaddr = self.server.accept()
        self.switch_sockets.append(clientsock)
        self.port_switch_dict[clientsock.getpeername()[1]]= Switch(len(self.port_switch_dict)+1)
        if forwarders[0]:
            try:
                print(str(clientaddr) + " has connected")
                self.input_list.append(clientsock)
                for i in range(number_of_controllers):
                    self.input_list.append(forwarders[i])
                    self.channels[i][clientsock] = forwarders[i]
                    self.channels[i][forwarders[i]] = clientsock
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
        self.switch_sockets.remove(self.s)
        del self.port_switch_dict[self.s.getpeername()[1]]
        for i in range(number_of_controllers):
            self.input_list.remove(self.channels[i][self.s])
            out = self.channels[i][self.s]
            # close the connection with remote server
            self.channels[i][self.s].close()
            # delete both objects from channel dict
            del self.channels[i][out]
            del self.channels[i][self.s]
        # close the connection with client
        self.s.close()


    def on_recv(self):
        data = self.data
        # here we can parse and/or modify the data before send forward
        if self.s in self.switch_sockets:
            temp_switch = self.port_switch_dict[self.s.getpeername()[1]]
            source = "Switch" + str(temp_switch.number)
            packet_info = Hyper_packet(data,source,self.port_switch_dict[self.s.getpeername()[1]])
            slice_no = packet_info.slice
            if slice_no:
                self.channels[slice_no-1][self.s].send(data)
                print('  - Forwarded to just Controller ' + str(slice_no))
                print('*****************************************')
            else:
                for i in range(number_of_controllers):
                    self.channels[i][self.s].send(data)
                print('  - Forwarded to ALL Controllers')
        else:
            for i in range(number_of_controllers):
                if self.s in self.controller_sockets[i]:
                    source = "Controller" + str(i+1)
                    packet_info = Hyper_packet(data, source)
                    self.channels[i][self.s].send(data)
                    break
        # for p in self.port_switch_dict.values():
        #     attr = vars(p)
        #     print(', '.join("%s: %s" % item for item in attr.items()))
       

if __name__ == '__main__':
        server = TheServer(hypervisor_address[0],hypervisor_address[1])
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print("Ctrl C - Stopping server")
            sys.exit(1)