import string
from pyof.v0x04.common.header import Header, Type
from pyof.v0x04.common.utils import unpack_message
from pyof.v0x04.common.flow_match import Match, OxmOfbMatchField, MatchType
from pyof.foundation.base import GenericType

class Slice(object):
    '''
    This object creates a slice for each controller
        slice_no: controller_no
        switches[]: list of switches
                    dpid, available_ports[], connection_port, flow_entry_counter
    '''
    def __init__(self, slice_no, c_addr):
        '''
        list of switch-port pairs e.g. {"swicth":1, "conn_port":1, "ports":[1,2,3],"flow_entry_counter":1}
        flow_entry_counter: increment at each flow entry added; decrement at each flow entry removed
        '''
        self.slice_no = slice_no
        self.controller_address = c_addr
        self.switches = [] #list of swicthes
        self.hosts = []

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
        self.dpid = '0'
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


        self.flow_entry_max = forwarder.flow_entry_max
        self.no_of_flow_entries = {}
        self.flow_match_entries = {}
        for i in range(1,forwarder.number_of_controllers+1):
            self.flow_match_entries[i] = []
            self.no_of_flow_entries[i] = 0
        
        # max packets buffered at once
        self.n_buffers = 0
        # number of tables supported by the datapath
        self.n_tables = 0

    def flow_add(self, packet_info, controller_id):
        if self.no_of_flow_entries[controller_id] < self.flow_entry_max:
            self.no_of_flow_entries[controller_id] += 1
            #print('Switch:{}, No of flows: {} for slice {}'.format(str(self.number), str(self.no_of_flow_entries[controller_id]), str(controller_id)))
            return True
        else:
            print("Raise flag for max entries")
            return False

    def flow_remove(self, packet_info, controller_id):
        self.no_of_flow_entries[controller_id] -= 1
        # print("Flow Removed for switch {} from slice {}".format(str(self.number), str(controller_id)))
        # print("New number of flows are {} ".format(str(self.no_of_flow_entries[controller_id])))
            
class Port(object):

    def __init__(self, multi_port):
        # this object is used in the switches dictionary 
        self.port_no = int(str(multi_port.port_no))
        self.name = str(multi_port.name)
        self.hw_addr = str(multi_port.hw_addr)
        self.connected_mac = None
        self.list_of_slices = []
        self.connected_ip = None