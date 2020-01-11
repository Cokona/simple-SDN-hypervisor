# Based on the implementation of the SimpleSwitch13
from operator import attrgetter
import networkx as nx
import time

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
FLOW_DEFAULT_IDLE_TIMEOUT = 10  # Idle Timeout value for flows


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
        self.switches = []

        self.arp_checker = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: None)))

        self.balance_link_load = False

        self.update_topo_thread = hub.spawn(self._print_topo)
        self.update_link_load_thread = hub.spawn(self._poll_link_load)
        self.reset_arp_checker = hub.spawn(self._reset_arp)

    @set_ev_cls(topo_event.EventHostAdd)
    def new_host_handler(self, ev):
        host = ev.host
        # self.logger.info("New %s detected", host)
        # Task 1: Add the new host with its MAC-address as a node to the graph.
        # Add also appropriate edges to connect it to the next switch

        # self.graph.add_node()
        self.graph.add_node(
            host.mac,
            **{
                'type': 'client'
            }
        )
        if (host.mac, host.port.dpid) not in self.graph.edges:
            self.graph.add_edge(host.mac, host.port.dpid, **{'link_load': 0.0, 'time': 0.0,
                                                             'old_num_bytes': 0, 'curr_speed': 1000000})
            self.graph.add_edge(host.port.dpid, host.mac, **{'port': host.port.port_no, 'link_load': 0.0, 'time': 0.0,
                                                             'old_num_bytes': 0, 'curr_speed': 1000000})

    @set_ev_cls(topo_event.EventSwitchEnter)
    def new_switch_handler(self, ev):
        switch = ev.switch
        self.switches.append(switch)
        # self.logger.info("New %s detected", switch)
        #  Task 1: Add the new switch as a node to the graph.
        # self.graph.add_node(   )
        self.graph.add_node(switch.dp.id, **{'type': 'sw'})

    def __get_port_speed(self, dpid, port_no, switches_list):
        for switch in switches_list:
            if switch.dp.id == dpid:
                return switch.dp.ports[port_no].curr
        self.logger.debug("No BW info for %s at %s" % (port_no, dpid))
        return 1  # default value

    @set_ev_cls(topo_event.EventLinkAdd)
    def new_link_handler(self, ev):
        link = ev.link
        # self.logger.info("New %s detected", link)
        #  Task 1: Add the new link as an edge to the graph
        # Make sure that you do not add it twice.
        # self.graph.add_edge()
        if (link.src.dpid, link.dst.dpid) not in self.graph.edges:
            self.graph.add_edge(link.src.dpid, link.dst.dpid,
                                **{'port': link.src.port_no,
                                   'link_load': 0.0,
                                   'time': 0.0,
                                   'old_num_bytes': 0,
                                   'curr_speed': self.__get_port_speed(link.src.dpid, link.src.port_no, self.switches)
                                   }
                                )

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
            # self.logger.info("Nodes: %s" % self.graph.nodes)
            # self.logger.info("Edges: %s" % self.graph.edges)
            hub.sleep(10)

    def _poll_link_load(self):
        """
        Sends periodically port statistics requests to the SDN switches. Period: 1s
        :return:
        """
        while True:
            for sw in self.switches:
                self._request_port_stats(sw.dp)
            hub.sleep(1)

    def _request_port_stats(self, datapath):
        # self.logger.info('send stats request: %016x', datapath.id)
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
            ev:
        Returns

        """
        body = ev.msg.body
        dpid = ev.msg.datapath.id

        out_str = ""
        for stat in sorted(body, key=attrgetter('port_no')):
            num_bytes = stat.rx_bytes + stat.tx_bytes
            new_time = time.time()
            # TODO Task 3: Update the load value of the corresponding edge in self.graph


            for edge_candidate in self.graph[dpid]:
                # self.logger.debug("%s %s %s" % (dpid, edge_candidate, self.graph[dpid][edge_candidate]))
                try:
                    if self.graph[dpid][edge_candidate]['port'] == stat.port_no:
                        delta_t = new_time - self.graph[dpid][edge_candidate]['time']
                        delta_bytes = num_bytes - self.graph[dpid][edge_candidate]['old_num_bytes']
                        speed = self.graph[dpid][edge_candidate]['curr_speed']
                        # load in bytes/sec
                        self.graph[dpid][edge_candidate]['link_load'] = 1.0 * delta_bytes / delta_t + 1
                        self.graph[dpid][edge_candidate]['time'] = new_time
                        self.graph[dpid][edge_candidate]['old_num_bytes'] = num_bytes

                        out_str += '%8x %s \t' % (stat.port_no, self.graph[dpid][edge_candidate]['link_load'])
                        break
                except KeyError:
                    pass
                    # self.logger.info(stat)
        # self.logger.info('datapath %s' % dpid)
        # self.logger.info('---------------- -------- '
        #                  '-------- -------- -------- '
        #                  '-------- -------- --------')
        # self.logger.info(out_str)

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
        path_out = []
        if balanced:
            # TODO Task 3: Implement load balanced routing
            path_tmp = nx.shortest_path(self.graph, src, dst, weight="link_load")
            self.logger.info('A Path was found!! : %s', path_tmp)             # DEBUG
            path_index = 0
            for dpid in path_tmp[:-1]:
                dp = topo_api.get_switch(self, dpid)[0].dp
                port = self.graph.edges[(dpid, path_tmp[path_index + 1])]['port']
                path_index += 1
                path_out.append({'dp': dp, 'port': port, 'dpid': dp.id})
        else:
            # Task 2: Determine path to destination using nx.shortest_path.
            path_tmp = nx.shortest_path(self.graph, src, dst, weight=None)  # weight = 1, Path weight = # Hops
            self.logger.info('A Path was found!! : %s', path_tmp)             # DEBUG
            path_index = 0
            for dpid in path_tmp[:-1]:
                # TODO Task 2: Convert to an appropriate representation
                dp = topo_api.get_switch(self, dpid)[0].dp
                port = self.graph.edges[(dpid, path_tmp[path_index + 1])]['port']
                path_index += 1
                path_out.append({'dp': dp, 'port': port, 'dpid': dp.id})
        self.logger.debug("Path: %s" % path_out)
        if len(path_out) == 0:
            raise PathCalculationError()
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

    def add_flow_for_path(self, parser, routing_path, pkt, nw_src, nw_dest, dl_src, in_port):
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

        port_previous_hop = in_port
        for hop in routing_path:  # The switches between the incoming switch and the server
            self.logger.debug("previous port: %s, this hop dp: %s" % (port_previous_hop, hop['dp'].id))
            # TODO Task 2: Determine match and actions
            if tcp_data:
                match = parser.OFPMatch(dl_type=0x0800, nw_dst=nw_dest,
                                        nw_src=nw_src, nw_proto=6, tp_src=tcp_data.src_port,
                                        in_port=port_previous_hop) #, dl_src=dl_src)
            elif udp_data:
                match = parser.OFPMatch(dl_type=0x0800, nw_dst=nw_dest,
                                        nw_src=nw_src, nw_proto=17, tp_src=udp_data.src_port,
                                        in_port=port_previous_hop) #, dl_src=dl_src)
            else:
                match = parser.OFPMatch(dl_type=0x0800, nw_dst=nw_dest,
                                        in_port=port_previous_hop, nw_src=nw_src) # , dl_src=dl_src)
            actions = [parser.OFPActionOutput(hop['port'], 0)]
            self.add_flow(hop['dp'], FLOW_DEFAULT_PRIO_FORWARDING, match, actions, None, FLOW_DEFAULT_IDLE_TIMEOUT)
            port_previous_hop = hop['port']

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

        # Get the path to the server
        routing_path = self.calculate_path_to_server(
            datapath.id, self.ip_to_mac.get(net_dst, eth_dst_in), balanced=True
        )
        # self.logger.info("Calculated path from %s-%s: %s" % (datapath.id, self.ip_to_mac.get(net_dst, eth_dst_in),
                                                            #  routing_path))
        self.add_flow_for_path(parser, routing_path, pkt, net_src, net_dst, eth.src, in_port)
        self.logger.debug("Installed flow entries FORWARDING (pub->priv)")

        actions_po = [parser.OFPActionOutput(routing_path[-1]["port"], 0)]
        out_po = parser.OFPPacketOut(datapath=routing_path[-1]['dp'],
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
            # Check if ARP-package from arp_src to arp_dst already passed this switch and drop or process accordingly
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
