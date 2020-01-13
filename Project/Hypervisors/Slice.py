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

    def __init__(self, dpid, out_port):
        self.dpid = dpid
        self.available_ports = []
        self.connected_port = out_port
        self.flow_entry_max = 20
        self.flow_entry_counter = 20

    def flow_add(self):
        if self.flow_entry_counter < self.flow_entry_max:
            self.flow_entry_counter += 1
        else:
            ##cannot write into the switch's flow table
            #send error msg back
            pass

    def flow_remove(self):
        if self.flow_entry_counter > 0:
            self.flow_entry_counter -= 1
        else:
            ##cannot remove from the switch's flow table
            #send error msg back
            pass