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
        # Swıtch number assıgned when ınıtıated ın the proxy_port_to_swıtch dıct ın maın 
        self.number = len(forwarder.proxy_port_switch_dict)+1
        self.dpid = None
        # thıs ıs added when we have a arp message - check hyper parser packet ın
        self.ports = {}
        # for checkıng duplıcate common messages
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
        # has a lıst of actıve buffer ıds
        self.buffer_flags = []


        self.flow_entry_max = 20
        self.flow_entry_counter = {}
        for i in range(1,forwarder.number_of_controllers):
            self.flow_entry_counter[i] = 0

    def flow_add(self, slice_no):
        if self.flow_entry_counter[slice_no] < self.flow_entry_max:
            self.flow_entry_counter[slice_no] += 1
            print('Switch:{}, No of flows: {} for slice {}'.format(str(self.number), str(self.flow_entry_counter[slice_no])))
        else:
            print("Raise flag for max entires")
            pass

    def flow_remove(self,slice_no):
        if self.flow_entry_counter > 0:
            self.flow_entry_counter -= 1
        else:
            ##cannot remove from the switch's flow table
            #send error msg back
            pass

class Port(object):

    def __init__(self, packet):
        # thıs object ıs ın the swıtches dıctıonary 
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
 
