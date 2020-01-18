import string


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

    def __init__(self,number):
        self.number = number
        self.dpid = None
        self.ports = {}
        #self.connected_port = out_port
        # self.flow_entry_max = 20
        # self.flow_entry_counter = 20

    # def flow_add(self):
    #     if self.flow_entry_counter < self.flow_entry_max:
    #         self.flow_entry_counter += 1
    #     else:
    #         ##cannot write into the switch's flow table
    #         #send error msg back
    #         pass

    # def flow_remove(self):
    #     if self.flow_entry_counter > 0:
    #         self.flow_entry_counter -= 1
    #     else:
    #         ##cannot remove from the switch's flow table
    #         #send error msg back
    #         pass

class Port(object):

    def __init__(self, packet):
        self.port_no = packet.in_port
        self.connected_mac = packet.mac_src
        self.list_of_slices = [packet.slice_no]
        self.connected_ip = packet.ip_src

    # # # # # # # # def update_mac_and_slice_no(self,mac):
    # # # # # # # #     # self.connected_mac = mac
    # # # # # # # #     # if self.connected_mac[0:2] == self.connected_mac[3:5]:
    # # # # # # # #     #     self.slice_no = string.ascii_uppercase.index(self.connected_mac[0]) + 1
    # # # # # # # #         # print("MADDDDDAAAAAAFFFFFAAAAAKKKKKKKKAAAAA")
    # # # # # # # #     # print("connected mac is {} with slice no {}".format(str(self.connected_mac), str(self.slice_no)))
    # # # # # # # #     pass
 
