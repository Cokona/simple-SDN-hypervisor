# Based on the implementation of the SimpleSwitch13
from operator import attrgetter
import networkx as nx
import time
import matplotlib.pyplot as plt

from ryu import cfg
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_0

from ryu.lib.mac import haddr_to_bin
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


class LoadBalancer(app_manager.RyuApp):
    """
    This class maintains the network state and fetches the CPU load of the servers. The load balancing decisions are
    triggered here and the routing paths are calculated
    """
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    _CONTEXTS = {}

    def __init__(self, *args, **kwargs):
        super(LoadBalancer, self).__init__(*args, **kwargs)
        self.name = 'LoadBalancer'
        self.mac_to_port = {}
        self.ip_to_mac = {}
        # Variables for the network topology
        self.graph = nx.DiGraph()
        self.hosts = []
        self.links = []
        self.switches = {}
        self.edges_saved = []

        self.arp_checker = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

        self.balance_link_load = False

        self.update_topo_thread = hub.spawn(self._print_topo)
        self.update_link_load_thread = hub.spawn(self._poll_link_load)
        self.reset_arp_checker = hub.spawn(self._reset_arp)

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
            self.logger.info("The ip of %s is %s", hostDict[host.mac], host.ipv4)
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

    def __get_port_speed(self, dpid, port_no, switches_list):
        for switch in switches_list:
            if switch.dp.id == dpid:
                return switch.dp.ports[port_no].curr
        self.logger.debug("No BW info for %s at %s" % (port_no, dpid))
        return 1  # default value

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

    def _reset_arp(self):
        hub.sleep(2)
        while True:
            self.arp_checker = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))
            hub.sleep(2)

    def _print_topo(self):
        """
        Prints a list of nodes and edges to the console
        For Debugging, Period 10s
        :return:
        """
        hub.sleep(15)
        while True:
            self.logger.info("Nodes: %s" % self.graph.nodes)
            self.logger.info("Edges: %s" % self.graph.edges)
            nx.draw_networkx(self.graph,with_labels=True)
            plt.draw()
            plt.show()
            # for (u, v, wt) in self.graph.edges.data('utilization'):
            #     self.logger.info("Edge %s utilization %s" % ((u,v), wt))
            hub.sleep(10)

    def _poll_link_load(self):
        """
        Sends periodically port statistics requests to the SDN switches. Period: 1s
        :return:
        """
        while True:
            for sw in self.switches.keys():
                self._request_port_stats(self.switches[sw])
            hub.sleep(1)

    def _request_port_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_NONE)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        """
        Calculates the link load based on the received port statistics. The values are stored as an attribute of the
        edges in the networkx DiGraph. [Bytes/Sec]/[Max Link Speed in Bytes]
        Args:
            ev:              ['timestamp', 'msg']
            ev.msg:          ['datapath', 'version', 'msg_type', 'msg_len', 'xid', 'buf', 'type', 'flags', 'body']
            ev.msg.datapath: ['ofproto', 'ofproto_parser', 'socket', 'address', 'is_active', 'send_q', '_send_q_sem', 'echo_request_interval', 
                             'max_unreplied_echo_requests', 'unreplied_echo_requests', 'xid', 'id', '_ports', 'flow_format', 'ofp_brick', 'state', 'ports']
        Returns
        """
        body = ev.msg.body
        dpid = ev.msg.datapath.id
        # self.logger.info('From DP: %d came the message : %s', dpid, body)
        for stat in sorted(body, key=attrgetter('port_no')):
            num_bytes = stat.rx_bytes + stat.tx_bytes
            new_time = time.time()
            # TODO Task 3: Update the load value of the corresponding edge in self.graph
            current_switch = 's' + str(dpid)
            # self.logger.info(self.graph.edges(current_switch))
            for (u, v) in self.graph.edges(current_switch):
                if self.graph[current_switch][v]['ports'][current_switch] == stat.port_no:
                    utilization = ((num_bytes - self.graph[current_switch][v]['bytes']) / (new_time - self.graph[current_switch][v]['time'])) + 1 
                    self.graph[current_switch][v]['utilization'] = utilization
                    self.graph[current_switch][v]['time'] = new_time
                    self.graph[current_switch][v]['bytes'] = num_bytes
                    return
                    
    def calculate_path_to_server(self, src, dst, balanced=False):
        """
        Returns the path of the flow
        Args:
            src: dpid of switch next to source host
            dst: dpid of switch next to destination host
            balanced: Indicates if the load on the links should be balanced
        Returns:
             list of hops (dict of dpid and outport) {'dp': XXX, 'port': YYY}
        """
        if dst == "ff:ff:ff:ff:ff:ff":
            self.logger.info('THIS IS A BROADCAST AND PATH RETURNS NONE')
            return None

        #self.logger.info('Look AT THE SOURCE' + str(src))
        src = 's'+str(src)
        dst = hostDict[str(dst)]

        path_out = []
        # TODO Task 3: Implement load balanced routing
        if balanced:
            weight = 'utilization'
        else:
            weight = 1
        # Task 2: Determine path to destination using nx.shortest_path.
        try:
            path_tmp = nx.shortest_path(self.graph, src, dst, weight=weight)  # weight = 1, Path weight = # Hops
            self.logger.info('A Path was found!! : %s', path_tmp)             # DEBUG
        except:
            self.logger.info("Path not found")
            path_tmp = []
        path_index = 0
        for dp_index in range(len(path_tmp)-1):
            # TODO Task 2: Convert to an appropriate representation
            src_dp = path_tmp[dp_index]
            dst_dp = path_tmp[dp_index+1]
            out_port = self.graph[src_dp][dst_dp]['ports'][src_dp]
            # self.logger.info("SRC: %s OUT_PORT: %s\nDST: %s " % (src_dp, out_port, dst_dp))
            path_out.append({"dp":src_dp, "port":out_port})
        self.logger.debug("Path: %s" % path_out)
        if len(path_out) == 0:
            #raise PathCalculationError()
            self.logger.info('Here was the problem')
        return path_out

    def add_flow(self, datapath, priority, match, actions, buffer_id=None, idle_timeout=0):
        """
        Installs a single rule on a switch given the match and actions
        Args:
            datapath:
            priority:
            match:
            actions:
            buffer_id:
            idle_timeout:

        Returns:

        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    idle_timeout=idle_timeout, priority=priority, match=match,
                                    actions=actions)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    idle_timeout=idle_timeout,
                                    match=match, actions=actions)
        datapath.send_msg(mod)

    def add_flow_for_path(self, parser, routing_path, pkt, nw_src, nw_dest, dl_src, dl_dst, in_port):
        """
        Installs rules on all switches on the given path to forward the flow
        Args:
            parser: OF parser object
            routing_path: List of dp objects with corresponding out port
            pkt: whole packet
            nw_src: ipv4 source address
            nw_dest: ipv4 destination address
            dl_src: eth source address
            in_port: input port of packet

        Returns:

        """
        tcp_data = pkt.get_protocol(tcp.tcp)
        udp_data = pkt.get_protocol(udp.udp)

        # port_previous_hop = in_port
        for hop in routing_path:  # The switches between the incoming switch and the server
            # self.logger.debug("previous port: %s, this hop dp: %s" % (port_previous_hop, hop['dp'].id))
            # TODO Task 2: Determine match and actions
            if tcp_data:
                match = parser.OFPMatch(dl_type=0x0800, nw_dst=nw_dest,
                                        nw_src=nw_src, nw_proto=6, tp_src=tcp_data.src_port) #, dl_src=dl_src)
            elif udp_data:
                match = parser.OFPMatch(dl_type=0x0800, nw_dst=nw_dest,
                                        nw_src=nw_src, nw_proto=17, tp_src=udp_data.src_port) #, dl_src=dl_src)
            else:
                match = parser.OFPMatch(dl_type=0x0800, nw_dst=nw_dest, nw_src=nw_src) # , dl_src=dl_src)
            actions = [parser.OFPActionOutput(hop['port'], 0)]
            self.add_flow(self.switches[hop['dp']], FLOW_DEFAULT_PRIO_FORWARDING, match, actions, None, FLOW_DEFAULT_IDLE_TIMEOUT_IP)
            # port_previous_hop = hop['port']
            

    def _handle_ipv4(self, datapath, in_port, pkt):
        """
        Handles an IPv4 packet. Calculates the route and installs the appropriate rules. Finally, the packet is sent
        out at the target switch and port.
        Args:
            datapath: DP object where packet was received
            in_port: ID of the input port
            pkt: The packet
        Output:
            -output on single port of the switch
        And installs flows to forward the packet on the port that is connected to the next switch/the target server

        Returns:
            SimpleSwitch forwarding indicator (True: simpleswitch forwarding), the (modified) packet to forward
        """
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # extract headers from packet
        eth = pkt.get_protocol(ethernet.ethernet)
        ipv4_data = pkt.get_protocol(ipv4.ipv4)

        eth_dst_in = eth.dst
        net_src = ipv4_data.src
        net_dst = ipv4_data.dst
        # self.logger.info(self.ip_to_mac.get(net_dst, eth_dst_in))         # DEBUG
        # Get the path to the server
        routing_path = self.calculate_path_to_server(
            datapath.id, self.ip_to_mac.get(net_dst, eth_dst_in), balanced=True
        )

        if routing_path is None:
            self.logger.info('There is No ROUTING_PATH')
            return

        # self.logger.info("Calculated path from %s-%s: %s" % (datapath.id, self.ip_to_mac.get(net_dst, eth_dst_in),
                                                            #  routing_path))
        self.add_flow_for_path(parser, routing_path, pkt, net_src, net_dst, eth.src, eth.dst, in_port)
        self.logger.debug("Installed flow entries FORWARDING (pub->priv)")

        actions_po = [parser.OFPActionOutput(routing_path[-1]["port"], 0)]
        out_po = parser.OFPPacketOut(datapath=self.switches[routing_path[-1]['dp']],
                                     buffer_id=ofproto.OFP_NO_BUFFER,
                                     in_port=in_port, actions=actions_po, data=pkt.data)

        datapath.send_msg(out_po)
        self.logger.debug("Packet put out at %s %s", datapath, routing_path[-1]["port"])

        return False, pkt

    def _handle_simple_switch(self, datapath, in_port, pkt, buffer_id=None, eth_dst=None):
        """
        Simple learning switch handling for non IPv4 packets.
        Args:
            datapath:
            in_port:
            pkt:
            buffer_id:
            eth_dst:

        Returns:

        """
        dpid = datapath.id
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if buffer_id is None:
            buffer_id = ofproto.OFP_NO_BUFFER

        eth = pkt.get_protocols(ethernet.ethernet)[0]
        if eth_dst is None:
            eth_dst = eth.dst
        dl_src = eth.src
        if dpid not in self.mac_to_port:
            self.mac_to_port[dpid] = {}
        self.logger.debug("M2P: %s", self.mac_to_port)
        # learn mac address
        self.mac_to_port[dpid][dl_src] = in_port
        self.logger.debug("packet in %s %s %s %s", dpid, in_port, dl_src, eth_dst)

        if eth_dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][eth_dst]
        elif eth_dst == 'ff:ff:ff:ff:ff:ff':
            self.logger.info("Broadcast packet at %s %s %s", dpid, in_port, dl_src)
            out_port = ofproto.OFPP_FLOOD
        else:
            self.logger.debug("OutPort unknown, flooding packet %s %s %s %s", dpid, in_port, dl_src, eth_dst)
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            match = parser.OFPMatch(in_port=in_port, dl_dst=haddr_to_bin(eth_dst))
            # verify if we have a valid buffer_id, if yes avoid to send both
            # flow_mod & packet_out
            if buffer_id != ofproto.OFP_NO_BUFFER:
                self.add_flow(datapath, FLOW_DEFAULT_PRIO_FORWARDING, match, actions, buffer_id,
                              FLOW_DEFAULT_IDLE_TIMEOUT)
            else:
                self.add_flow(datapath, FLOW_DEFAULT_PRIO_FORWARDING, match, actions, None,
                              FLOW_DEFAULT_IDLE_TIMEOUT)
        data = None
        if buffer_id == ofproto.OFP_NO_BUFFER:
            data = pkt.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        """
        Is called if a packet is forwarded to the controller. Packet handling is done here.
        We drop LLDP and IPv6 packets and pre-install paths for IPv4 packets. Other packets are handled by simple learning switch
        Args:
            ev: OF PacketIn event
        Returns:

        """
        # If you hit this you might want to increase
        # the "miss_send_length" of your switch
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)

        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.in_port

        pkt = packet.Packet(msg.data)

        eth = pkt.get_protocol(ethernet.ethernet)
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return

        arp_header = pkt.get_protocol(arp.arp)
        ipv4_header = pkt.get_protocol(ipv4.ipv4)
        ipv6_header = 34525 # TODO Check if same handling as for ipv4 should be implemented, or should be dropped (currently dropped)
        if arp_header:  # we got an ARP
            # Learn src ip to mac mapping and forward
            if arp_header.src_ip not in self.ip_to_mac:
                self.ip_to_mac[arp_header.src_ip] = arp_header.src_mac
            eth_dst = self.ip_to_mac.get(arp_header.dst_ip, None)
            arp_dst = arp_header.dst_ip
            arp_src = arp_header.src_ip
            current_switch = datapath.id

            # Check if ARP-package from arp_src to arp_dst already passed this switch.
            if self.arp_checker[current_switch][arp_src][arp_dst]:
                self.logger.debug("ARP package known and therefore dropped")
                return
            else:
                self.arp_checker[current_switch][arp_src][arp_dst] = 1
                self.logger.debug("Forwarding ARP to learn address, but dropping all consecutive packages.")
                self._handle_simple_switch(datapath, in_port, pkt, msg.buffer_id, eth_dst)
        elif ipv4_header:  # IP packet -> load balanced routing
            self._handle_ipv4(datapath, in_port, pkt)
        elif ipv6_header:
            return
        else:
            self._handle_simple_switch(datapath, in_port, pkt, msg.buffer_id)
