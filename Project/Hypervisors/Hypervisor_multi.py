#!/usr/bin/python
# This is a simple port-forward / proxy, written using only the default python

import socket
import select
import time
import sys
from helpers import Switch, Slice
import pyof
from pyof.v0x04.common.utils import unpack_message
from hyper_parser_kimon import Packet_controller, Packet_switch


# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 1024
delay = 0.0001
number_of_controllers = int(sys.argv[1])
controller_addresses = []

FLOOD_PORT = 4294967291

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
            print('EXCEPTION : ' + str(e))
            return False


class TheServer:
    input_list = []
    switch_sockets = []
    controller_sockets = []
    channels = []
    for i in range(number_of_controllers):
        channels.append({})
        controller_sockets.append([])
    proxy_port_switch_dict = {}

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
        self.proxy_port_switch_dict[clientsock.getpeername()[1]]= Switch(len(self.proxy_port_switch_dict)+1)
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
        del self.proxy_port_switch_dict[self.s.getpeername()[1]]
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
            temp_switch = self.proxy_port_switch_dict[self.s.getpeername()[1]]
            packet_info = Packet_switch(data,self.proxy_port_switch_dict[self.s.getpeername()[1]])
            slice_no = packet_info.slice_no
            if slice_no:
                self.channels[slice_no-1][self.s].send(data)
                print('Src:  SWITCH{},  Dst:  CONTROLLER{},  Packet_type: {}'.format(
                                                                    str(temp_switch.number),str(slice_no),str(packet_info.of_type)))
            else:
                for i in range(number_of_controllers):
                    self.channels[i][self.s].send(data)
                print('Src:  SWITCH{},  Dst:  CONTROLLERs,  Packet_type: {}'.format(
                                                                    str(temp_switch.number),str(packet_info.of_type)))
                try:
                    temp_switch.common_message_flag[temp_switch.reset_message_flag[packet_info.of_type]] = True
                except:
                    pass
        else:
            for i in range(number_of_controllers):
                if self.s in self.controller_sockets[i]:
                    packet_info = Packet_controller(data, i)
                    switch_to_send = self.proxy_port_switch_dict[self.channels[i][self.s].getpeername()[1]]
                    controller_id = i+ 1
                    if self.check_for_permission(packet_info, switch_to_send, controller_id):
                            flag_to_send = switch_to_send.common_message_flag.get(packet_info.of_type, None)
                            if flag_to_send is None:
                                self.channels[i][self.s].send(data)
                                print('Src:  Controller{},  Dst:  SWITCH{},  type: {}'.format(
                                                                        str(controller_id),str(switch_to_send.number),str(packet_info.of_type)))
                            elif flag_to_send is False:
                                self.proxy_port_switch_dict[self.channels[i][self.s].getpeername()[1]].common_message_flag[packet_info.of_type] = True   
                                self.channels[i][self.s].send(data)
                                print('Src:  Controller{},  Dst:  SWITCH{},  type: {}'.format(
                                                                        str(controller_id),str(switch_to_send.number),str(packet_info.of_type))) 
                            else:
                                print('BLOCKED :- Src:  Controller{},  Dst:  SWITCH{},  type: {}'.format(
                                                                        str(controller_id),str(switch_to_send.number),str(packet_info.of_type)))

        # for p in self.proxy_port_switch_dict.values():
        #     attr = vars(p)
        #     print(', '.join("%s: %s" % item for item in attr.items()))


    def check_for_permission(self, packet_info, switch_to_send, controller_id):
        port_to_send = packet_info.out_port                         # Switches output port to send or add flowmod
        if port_to_send and port_to_send != FLOOD_PORT:             # if Packet_out/Flow_mod/Stats_request
            port = switch_to_send.ports.get(port_to_send, None)     
            if port:                                                # If Port exists in the switch
                if controller_id in port.list_of_slices:                     # If port has the registered slice (Happens with ARP messages)
                    return True
                else:
                    return False
        else:
            return True
    



def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)
       
if __name__ == '__main__':
        server = TheServer(hypervisor_address[0],hypervisor_address[1])
        sys.excepthook = show_exception_and_exit      
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print("Ctrl C - Stopping server")
            sys.exit(1)