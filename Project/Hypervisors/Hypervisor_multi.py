#!/usr/bin/python
# This is a simple port-forward / proxy, written using only the default python

import socket
import select
import time
import sys
from helpers import Switch, Slice
import pyof
from pyof.v0x04.common.utils import unpack_message
from pyof.v0x04.common.header import Header, Type
from hyper_parser_kimon import Packet_controller, Packet_switch
import queue
from tkinter import *
from yash_gui_test import Gui
import threading

# Changing the buffer_size and delay, you can improve the speed and bandwidth.
# But when buffer get to high or delay go too down, you can broke things
buffer_size = 1024
delay = 0.0001


number_of_controllers = int(sys.argv[1])
number_of_switches =  int(sys.argv[2])




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
    
    def __init__(self, host, port,master):
        self.master = master
        self.queue = queue.Queue()
        self.number_of_controllers = number_of_controllers
        self.number_of_switches = number_of_switches
        self.flow_entry_max =5
        self.input_list = []
        self.switch_sockets = []
        self.controller_sockets = []
        self.channels = []
        for _ in range(self.number_of_controllers):
            self.channels.append({})
            self.controller_sockets.append([])
        self.proxy_port_switch_dict = {}
        self.mac_add = []
        self.temp_switch = None
        
        # Here we create the server instance and bind it to port 
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(200)     # !NOTE Reconsider 200
        self.gui = Gui(self.master, self.queue,self.number_of_controllers,self.number_of_switches,self.proxy_port_switch_dict.values(),self.flow_entry_max)
        # gui.mainloop()
        self.periodicCall()
        
    def periodicCall(self):
        """
        Check every 100 ms if there is something new in the queue.
        """
        switch_list = list(self.proxy_port_switch_dict.values())
        switch_list.sort(key=lambda x : int(x.dpid), reverse=False)
        for switcher in switch_list:
            print(switcher.dpid)
        self.queue.put(switch_list)
        self.gui.processIncoming()
        self.master.after(5000, self.periodicCall)

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
        for i in range(self.number_of_controllers):
            forwarders.append(Forward().start(controller_addresses[i][0], controller_addresses[i][1]))
            self.controller_sockets[i].append(forwarders[i])
        clientsock, clientaddr = self.server.accept()
        self.switch_sockets.append(clientsock)
        self.proxy_port_switch_dict[clientsock.getpeername()[1]]= Switch(self)
        if forwarders[0]:
            try:
                print(str(clientaddr) + " has connected")
                self.input_list.append(clientsock)
                for i in range(self.number_of_controllers):
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
        for i in range(self.number_of_controllers):
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
            self.temp_switch = self.proxy_port_switch_dict[self.s.getpeername()[1]]
            packet_info = Packet_switch(data,self)
            slice_no = packet_info.slice_no
            if packet_info.buffer_id:
                self.temp_switch.buffer_flags.append(packet_info.buffer_id)
            if slice_no:
                self.channels[slice_no-1][self.s].send(data)
                print('Src:  SWITCH{},  Dst:  CONTROLLER{},  Packet_type: {}'.format(
                                                                    str(self.temp_switch.number),str(slice_no),str(packet_info.of_type)))
            else:
                if packet_info.of_type is Type.OFPT_FLOW_REMOVED:    # special case of Flow-Removed
                    check_for_flow_remove_flag = self.update_counters(self, packet_info)
                    if check_for_flow_remove_flag[0]:
                        self.channels[check_for_flow_remove_flag[1]-1][self.s].send(data)

                else:
                    for i in range(self.number_of_controllers):
                        self.channels[i][self.s].send(data)
                    print('Src:  SWITCH{},  Dst:  CONTROLLERs,  Packet_type: {}'.format(
                                                                        str(self.temp_switch.number),str(packet_info.of_type)))
                    try:
                        self.temp_switch.common_message_flag[self.temp_switch.reset_message_flag[packet_info.of_type]] = False
                    except:
                        pass
        else:
            for i in range(self.number_of_controllers):
                if self.s in self.controller_sockets[i]:
                    controller_id = i + 1
                    self.temp_switch = self.proxy_port_switch_dict[self.channels[i][self.s].getpeername()[1]]
                    packet_info = Packet_controller(data, controller_id, self)
                    # This checks for the list_of_slices to see if there is permission to send - Is it of the same slice or not
                    if self.check_for_permission(packet_info,controller_id):
                        ''' 
                        If flag_to_drop_common is None:    We do not have a conflicting COMMON packet.
                        If flag_to_drop_common is False:   This is the first conflicting packet, send and set flag to True
                        If flag_to_drop_common is True:    This is NOT the first instance of the conflicting COMMON packet, so duplicate message dropped
                        If flag_to_drop_buf_id is True:    This packet_out commands to send a message that has been cleared from the switch buffer, it is dropped
                        If flag_to_drop_buf_id is False:   This lets the message be sent if it doesn't have a buffer_id, or the buffer_id'ed message has been sent already
                        '''
                        flag_to_drop_common = self.temp_switch.common_message_flag.get(packet_info.of_type, None)
                        flag_to_drop_buf_id = self.check_for_duplicate_buf_id(packet_info)
                        if flag_to_drop_common is None:
                            if not flag_to_drop_buf_id:
                                if self.update_counters(packet_info,controller_id=controller_id):
                                    self.channels[i][self.s].send(data)
                                    print('Src:  Controller{},  Dst:  SWITCH{},  type: {}'.format(
                                            str(controller_id),str(self.temp_switch.number),str(packet_info.of_type)))
                        elif flag_to_drop_common is False:
                            self.proxy_port_switch_dict[self.channels[i][self.s].getpeername()[1]].common_message_flag[packet_info.of_type] = True   
                            self.channels[i][self.s].send(data)
                            print('Src:  Controller{},  Dst:  SWITCH{},  type: {}'.format(
                                    str(controller_id),str(self.temp_switch.number),str(packet_info.of_type)))
                        else:
                            print('Duplicate Message Dropped - Src:  Controller{},  Dst:  SWITCH{},  type: {}'.format(
                                    str(controller_id),str(self.temp_switch.number),str(packet_info.of_type)))
                            pass
                    else:
                        print("Access Denied: from CONTR{} to port{} of Switch{} of type:{}".format(
                                str(controller_id), str(packet_info.out_port), str(self.temp_switch.number), str(packet_info.of_type)))
        

    def check_for_permission(self, packet_info, controller_id):
        '''
        This function checks flow_mod and Packet_out messages for the slices
        This will return a True (permission to send) if the message.out_port has the slice which we are sending from.
        Switches output port to send or add flowmod
        '''
        
        port_to_send = packet_info.out_port
        #if packet is one of: Packet_out/Flow_mod/Stats_request AND out_port is not FLOOD
        if port_to_send and port_to_send != FLOOD_PORT:
            port = self.temp_switch.ports.get(port_to_send, None)
            # If Port has been registered in the switch
            if port:
                # If port has the registered slice (it is first registered with ARP messages)
                if controller_id in port.list_of_slices:
                    return True
                else:
                    return False
        else:
            return True

    def check_for_duplicate_buf_id(self, packet_info):
        '''
        This fucntion checks for messages that have a buffer_ID and are sent multiple times, so we want to drop all but the first instacnce of this
        This fucntion is only called when a message arrives from the controller, so it can be a packet_out but not a packet_in
        If there is a buffer_id it will check if this message has been received and forwarded before
        If yes it will return a flag_to_drop_buf_id as True
        If no it will return a  and remove the buffer_id from the list
        '''
        if packet_info.buffer_id:
            if packet_info.buffer_id not in self.temp_switch.buffer_flags:
                return True
            else:  # ADD COUNTER
                self.temp_switch.buffer_flags.remove(packet_info.buffer_id)
                return False
        else:
            return False

    def update_counters(self, packet_info,controller_id=None):
        if packet_info.of_type is Type.OFPT_FLOW_MOD:
            return self.temp_switch.flow_add(packet_info,controller_id)
        elif packet_info.of_type is Type.OFPT_FLOW_REMOVED:
            return self.temp_switch.flow_remove(packet_info)
        else:
            return True


def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)
       
if __name__ == '__main__':
    root = Tk()
    server = TheServer(hypervisor_address[0],hypervisor_address[1],root)
    sys.excepthook = show_exception_and_exit
    thread1 = threading.Thread(target=server.main_loop)      
    try:
        thread1.start()
        root.mainloop()
    except KeyboardInterrupt:
        print("Ctrl C - Stopping server")
        sys.exit(1)