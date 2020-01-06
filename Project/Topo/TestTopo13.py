# Based on the implementation of the SimpleSwitch13
from operator import attrgetter
import networkx as nx
import time
import matplotlib.pyplot as plt

from ryu import cfg
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_4
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet, arp, ipv4, tcp, udp, ether_types

from ryu.topology import api as topo_api
from ryu.topology import event as topo_event

from collections import defaultdict

CONF = cfg.CONF
FLOW_DEFAULT_PRIO_FORWARDING = 10
TABLE_ROUTING = 0
FLOW_DEFAULT_IDLE_TIMEOUT = 2       # Idle Timeout value for flows
FLOW_DEFAULT_IDLE_TIMEOUT_IP = 10   # Idle Timeout value for Ip paths
MAX_LINK_CAPACITY = 1000            # Max link capacity 1 Gbps

hostDict = {'aa:aa:aa:aa:aa:01': 'h1', 'aa:aa:aa:aa:aa:03': 'h3', 'aa:aa:aa:aa:aa:05': 'h5',  
            'aa:aa:aa:aa:aa:02': 'h2', 'aa:aa:aa:aa:aa:04': 'h4', 'aa:aa:aa:aa:aa:06': 'h6'}

class PathCalculationError(Exception):
    pass


class HyperVizor(app_manager.RyuApp):
    """
    This class maintains the network state and fetches the CPU load of the servers. The load balancing decisions are
    triggered here and the routing paths are calculated
    """
    OFP_VERSIONS = [ofproto_v1_4.OFP_VERSION]

    _CONTEXTS = {}

    def __init__(self, *args, **kwargs):
        super(HyperVizor, self).__init__(*args, **kwargs)
        self.name = 'Hypervizor'
        self.mac_to_port = {}
        self.ip_to_mac = {}
        self.no_of_subnets = 2
        self.subnet_mask = 24
        # Variables for the network topology
        self.graph = nx.DiGraph()
        self.hosts = []
        self.links = []
        self.switches = {}
        self.edges_saved = []

       # self.arp_checker = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

        #self.balance_link_load = False

        self.update_topo_thread = hub.spawn(self._print_topo)
       # self.update_link_load_thread = hub.spawn(self._poll_link_load)
        #self.reset_arp_checker = hub.spawn(self._reset_arp)

    @set_ev_cls(topo_event.EventHostAdd)
    def new_host_handler(self, ev):
        '''
        host = ['port', 'mac', 'ipv4', 'ipv6']
        '''
        host = ev.host
        # self.logger.info("New %s detected", host)
        # self.logger.info("LOOOOOKKKK  -  " + str(host.__dict__.keys()))

        # Task 1: Add the new host with its MAC-address as a node to the graph.
        # Add also appropriate edges to connect it to the next switch
        if host.mac in hostDict.keys():
            self.graph.add_node(hostDict[host.mac])
            current_switch = 's' + str(host.port.dpid)
            self.graph.add_edge(hostDict[host.mac],current_switch, ports= {hostDict[host.mac]: 1, current_switch: host.port.port_no}, 
                                time=time.time(), bytes=0, utilization=0)
            self.graph.add_edge(current_switch, hostDict[host.mac], ports= {hostDict[host.mac]: 1, current_switch: host.port.port_no}, 
                                time=time.time(), bytes=0, utilization=0)

    @set_ev_cls(topo_event.EventSwitchEnter)
    def new_switch_handler(self, ev):
        '''
        switch.dp = ['ofproto', 'ofproto_parser', 'socket', 'address', 'is_active', 'send_q', '_send_q_sem', 
                    'echo_request_interval', 'max_unreplied_echo_requests', 'unreplied_echo_requests', 'xid', 
                    'id', '_ports', 'flow_format', 'ofp_brick', 'state', 'ports']
        switch.ports = LIST OF: ['dpid', '_ofproto', '_config', '_state', 'port_no', 'hw_addr', 'name']
        '''
        switch = ev.switch
        dp = switch.dp
        ports = switch.ports
        # self.logger.info("New %s detected", switch)
        #  Task 1: Add the new switch as a node to the graph.
        self.graph.add_node('s' + str(dp.id))
        self.switches['s' + str(dp.id)] = switch.dp

    @set_ev_cls(topo_event.EventLinkAdd)
    def new_link_handler(self, ev):
        '''
        link = ['src', 'dst']
        link.src = ['dpid', '_ofproto', '_config', '_state', 'port_no', 'hw_addr', 'name']
        '''
        link = ev.link
        # self.logger.info("New %s detected", link)
        #  Task 1: Add the new link as an edge to the graph
        # Make sure that you do not add it twice.
        switch1 = 's' + str(link.src.dpid)
        switch2 = 's' + str(link.dst.dpid)  
        self.graph.add_edge(switch1, switch2, ports={switch1: link.src.port_no, switch2: link.dst.port_no},
         time=time.time(), bytes=0, utilization=0)

    def _print_topo(self):
        """
        Prints a list of nodes and edges to the console
        For Debugging, Period 10s
        :return:
        """
        hub.sleep(15)
        while True:
            #self.logger.info("Nodes: %s" % self.graph.nodes)
            #self.logger.info("Edges: %s" % self.graph.edges)
            #nx.draw_networkx(self.graph,with_labels=True)
            #plt.draw()
            #plt.show()
            # for (u, v, wt) in self.graph.edges.data('utilization'):
            #     self.logger.info("Edge %s utilization %s" % ((u,v), wt))
            for sub in self.ip_to_mac.keys():
                self.logger.info("Subnet %s hosts are : %s ", sub, list(map(hostDict.get,self.ip_to_mac[sub].values())))
            for switch in self.mac_to_port.keys():
                self.logger.info("Switch %s : ", switch)
                for sub in self.ip_to_mac.keys():
                    self.logger.info("Subnet %s: ports are %s",sub, list(self.mac_to_port[switch][mac] for mac in self.mac_to_port[switch].keys() if mac in self.ip_to_mac[sub].values()))
            hub.sleep(10)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install table-miss flow entry
        #
        # We specify NO BUFFER to max_len of the output action due to
        # OVS bug. At this moment, if we specify a lesser number, e.g.,
        # 128, OVS will send Packet-In with invalid buffer_id and
        # truncated packet data. In that case, we cannot output packets
        # correctly.  The bug has been fixed in OVS v2.1.0.
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)


    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    def get_subnet(self,ip_add):
        seperator = "."
        return seperator.join(ip_add.split(seperator)[:int(self.subnet_mask/8)])

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        ipv4_data = pkt.get_protocols(ipv4.ipv4)
        arp_header = pkt.get_protocols(arp.arp)
        

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src


        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})


        # self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

        # learn a mac address to avoid FLOOD next time.
        if src in hostDict.keys():
            self.mac_to_port[dpid][src] = in_port   # The 1.0 version--> msg.in_port
        if arp_header:  # we got an ARP
        # Learn src ip to mac mapping and forward
            subnet = self.get_subnet(arp_header.src_ip)
            self.ip_to_mac.setdefault(subnet, {})
            if arp_header.src_ip not in self.ip_to_mac[subnet]:
                self.ip_to_mac[subnet][arp_header.src_ip] = arp_header.src_mac

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if msg.buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, 1, match, actions, msg.buffer_id)
                return
            else:
                self.add_flow(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPortStatus, MAIN_DISPATCHER)
    def _port_status_handler(self, ev):
        msg = ev.msg
        reason = msg.reason
        port_no = msg.desc.port_no

        ofproto = msg.datapath.ofproto
        if reason == ofproto.OFPPR_ADD:
            self.logger.info("port added %s", port_no)
        elif reason == ofproto.OFPPR_DELETE:
            self.logger.info("port deleted %s", port_no)
        elif reason == ofproto.OFPPR_MODIFY:
            self.logger.info("port modified %s", port_no)
        else:
            self.logger.info("Illeagal port state %s %s", port_no, reason)