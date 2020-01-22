import string
from pyof.v0x04.common.header import Header, Type

class Slice(object):
    
    #create a slice for each controller
    '''
    slice_no: controller_no
    switches[]: list of switches
                dpid, available_ports[], connection_port, flow_entry_counter
    '''
    def __init__(self, slice_no, c_addr):

        self.slice_no = slice_no
        self.controller_address = c_addr
        self.switches = [] #list of swicthes
        self.hosts = []

        #list of switch-port pairs e.g. {"swicth":1, "conn_port":1, "ports":[1,2,3],"flow_entry_counter":1}
        # flow_entry_counter: increment at each flow entry added; decrement at each flow entry removed
    
    def switch_connected(self, dpid, port):
        if dpid not in self.switches:
            #self.switches += dpid
            #self.switches_ports += {"switch":dpid, "conn_port":port, "ports":[port],"flow_entry_counter":10}
            #initial upper bound of flow entries set to each switches for each slice
            pass

class Switch(object):

    def __init__(self,forwarder):
        # Switch number assigned when initiated in the proxy_port_to_switch dict in main 
        self.number = len(forwarder.proxy_port_switch_dict)+1
        self.dpid = None
        # this is added when we have a arp message - check hyper parser packet in
        self.ports = {}
        # for checking duplicate common messages
        self.common_message_flag = {Type.OFPT_HELLO:False,
                                    Type.OFPT_ERROR:False,
                                    Type.OFPT_FEATURES_REQUEST:False,
                                    Type.OFPT_PORT_STATUS:False, 
                                    Type.OFPT_MULTIPART_REQUEST:False,
                                    Type.OFPT_ECHO_REPLY:False}
        self.reset_message_flag = {Type.OFPT_HELLO:Type.OFPT_HELLO,
                                    Type.OFPT_FEATURES_REPLY:Type.OFPT_FEATURES_REQUEST,
                                    Type.OFPT_MULTIPART_REPLY:Type.OFPT_MULTIPART_REQUEST,
                                    Type.OFPT_ECHO_REQUEST:Type.OFPT_ECHO_REPLY}
        # has a list of active buffer ids
        self.buffer_flags = []


        self.flow_entry_max = 20
        # self.flow_entry_counter = {}
        self.flow_match_entries = {}
        for i in range(1,forwarder.number_of_controllers+1):
            self.flow_match_entries[i] = []

    def flow_add(self, packet_info,controller_id):
        no_of_flow_entries = len(self.flow_match_entries[controller_id])
        if no_of_flow_entries < self.flow_entry_max:
            if packet_info.match_field:
                if packet_info.match_field not in self.flow_match_entries[controller_id]:
                    self.flow_match_entries[controller_id].append(packet_info.match_field)
                    no_of_flow_entries = len(self.flow_match_entries[controller_id])
                    print('Switch:{}, No of flows: {} for slice {}'.format(str(self.number), str(no_of_flow_entries), str(controller_id)))
                else:
                    print("A flowmod with the same exact match fields is being added ????????? CHECK IT OUT")
            else: 
                print("Flow_add error, This message does not have a match field to be added")
        else:
            print("Raise flag for max entires")
            pass

    def flow_remove(self,packet_info):
        for slice_no_from_enries in range(1,len(self.flow_match_entries)+1):
            if packet_info.match_field in self.flow_match_entries[slice_no_from_enries]:
                break
            elif slice_no_from_enries is len(self.flow_match_entries):
                print('There is a problem with the flow remove logic - Trying to find the slice')

        no_of_flow_entries = len(self.flow_match_entries[slice_no_from_enries])

        if no_of_flow_entries > 0:
            if packet_info.match_field in self.flow_match_entries[slice_no_from_enries]:
                self.flow_match_entries[slice_no_from_enries].remove(packet_info.match_field)
                print("Flow Removed for switch {} from slice {}".format(str(self.number), str(slice_no_from_enries)))
                print("New number of flows are {} ".format(str(len(self.flow_match_entries[slice_no_from_enries]))))
            else:
                ##cannot remove from the switch's flow table
                #send error msg back
                print("SIGNIFICANT ERROR, SWITCH{} is trying to remove flow from slice{} that doesn't match the one in its entries!!!".format(
                    str(self.number),str(slice_no_from_enries)))
                pass
        else:
            print("Flow_remove DOES NOT HAVE any entries to remove")
            pass

class Port(object):

    def __init__(self, packet):
        # this object is in the switches dictionary 
        self.port_no = packet.in_port
        self.connected_mac = packet.mac_src
        self.list_of_slices = [packet.slice_no]
        self.connected_ip = packet.ip_src


        # shıt reserved for mac fılterıng

    # # # # # # # # def update_mac_and_slice_no(self,mac):
    # # # # # # # #     # self.connected_mac = mac
    # # # # # # # #     # if self.connected_mac[0:2] == self.connected_mac[3:5]:
    # # # # # # # #     #     self.slice_no = string.ascii_uppercase.index(self.connected_mac[0]) + 1
    # # # # # # # #         # print("MADDDDDAAAAAAFFFFFAAAAAKKKKKKKKAAAAA")
    # # # # # # # #     # print("connected mac is {} with slice no {}".format(str(self.connected_mac), str(self.slice_no)))
    # # # # # # # #     pass
 
