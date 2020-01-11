# Copyright (C) 2011 Nippon Telegraph and Telephone Corporation.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
An OpenFlow 1.0 L2 learning switch implementation.
"""

from operator import attrgetter

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER,DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import tcp
from ryu.lib import hub
from ryu.ofproto import ofproto_v1_0_parser


class SimpleSwitch(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.datapaths = {}
        # KEY: First value is the switch number, second one is the port number, VALUE is the data transmited 
        # Solution is only for students
        self.student_data_counter = {(3,2):0,(3,3):0,(6,2):0,(6,3):0}
        self.student_total_data_counter = {(3,2):0,(3,3):0,(6,2):0,(6,3):0}
        self.student_mac_mapping = {(3,2):'00:00:00:00:00:03',(3,3):'00:00:00:00:00:04',(6,2):'00:00:00:00:00:07',(6,3):'00:00:00:00:00:08'}
        self.prof_mac_mapping = {(2,2):'00:00:00:00:00:01',(2,3):'00:00:00:00:00:02',(5,2):'00:00:00:00:00:05',(5,3):'00:00:00:00:00:06'}
        self.prof_data_counter = {(2,2):0,(2,3):0,(5,2):0,(5,3):0}
        self.prof_total_data_counter = {(2,2):0,(2,3):0,(5,2):0,(5,3):0}
        self.monitor_thread = hub.spawn(self._monitor)
        self.student_sw = [3, 6]
        self.professor_sw = [2, 5]
        self.student_time_limit = 60
        self.professor_time_limit = 120
        self.student_data_limit = 1 * 10**9 # In bytes
        self.prof_data_limit = 5 * 10**9 # In bytes

    #Registring all datapaths for monitor pooling
    @set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
                #self.data_counter[datapath.id] = 0
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]
                #del self.data_counter[datapath.id]

    def add_flow(self, datapath, in_port, dst, actions):
        ofproto = datapath.ofproto

        match = datapath.ofproto_parser.OFPMatch(
            in_port=in_port, dl_dst=haddr_to_bin(dst))

        mod = datapath.ofproto_parser.OFPFlowMod(
            datapath=datapath, match=match, cookie=0,
            command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
            priority=ofproto.OFP_DEFAULT_PRIORITY,
            flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
        datapath.send_msg(mod)
    
    #Task 3a: Requesting port stats for a specific datapath
    def _request_stats(self, datapath):
        # self.logger.debug('send stats request: %016x', datapath.id)

        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        req = ofp_parser.OFPPortStatsRequest(datapath, 0, ofp.OFPP_NONE)
        datapath.send_msg(req)
   
    
    #Task 1: Write a function which checks if hosts have permission to communicate with each other
    #e.g. you can use MAC addresses of source and destination
    def check_permission(self, src_mac, dst_mac):
        student_macs = ['00:00:00:00:00:03', 
                        '00:00:00:00:00:04', 
                        '00:00:00:00:00:07', 
                        '00:00:00:00:00:08']

        professor_macs = ['00:00:00:00:00:01', 
                          '00:00:00:00:00:02', 
                          '00:00:00:00:00:05', 
                          '00:00:00:00:00:06']

        # If it is ARP let it pass
        if dst_mac == 'ff:ff:ff:ff:ff:ff':
             return True
        # If both source and destination are students, we grant premission
        if src_mac in student_macs and dst_mac in student_macs:
            return True
        # If both source and destination are professors, we grant premission
        if src_mac in professor_macs and dst_mac in professor_macs:
            return True
        # If previous cases are not satisfied, return false
        #print('Permission not granted!')
        return False
	
    
    #Task 2 - Blocking traffic based on TCP port
    #Notes: - add flow rules with higher priority to drop the packets
    #       - take care of timer of flow installation
    #       - for traffic differen
    def block_traffic(self,port,dp):
        ofproto = dp.ofproto
        # We need to specify that it is IP packet so dl_type = 0x0800, and also we need to specify that it is TCP packet as well so nw_proto = 6
        match = ofproto_v1_0_parser.OFPMatch(dl_type = 0x0800,nw_proto = 6,tp_dst=port)
        # Default action is to drop, hence, we can leave it empty 
        actions = [] 
        # Highers prio in OF is 65535, hence we set it to this value
        highest_prio = 65535
        # We just need to add these rules once, hance we set the timer to zero, which means the rule wont be deleted
        idle_timer = 0
        hard_timer = 0
        msg = dp.ofproto_parser.OFPFlowMod(dp,
                                priority = highest_prio,
                                idle_timeout = idle_timer,
                                hard_timeout = hard_timer,
                                command = ofproto.OFPFC_ADD,
                                match = match,
                                actions = actions
                                )
        dp.send_msg(msg)

    def limit_host_traffic_on_sw_port(self,port,dp,timer,mac_dst):
        ofproto = dp.ofproto
        # We need to specify that it is IP packet so dl_type = 0x0800, and also we need to specify that it is TCP packet as well so nw_proto = 6
        match_in = ofproto_v1_0_parser.OFPMatch(in_port = port)
        # Default action is to drop, hence, we can leave it empty 
        actions = [] 
        # Block for certain amount of time
        highest_prio = 65534
        msg_in = dp.ofproto_parser.OFPFlowMod(dp,
                                priority = highest_prio,
                                hard_timeout = timer,
                                command = ofproto.OFPFC_ADD,
                                match = match_in,
                                actions = actions
                                )

        # If host is a destination, block him on all switches
        match_out = ofproto_v1_0_parser.OFPMatch(dl_dst = mac_dst)
        dp.send_msg(msg_in)
        for datapath in self.datapaths.values():
            msg_out = datapath.ofproto_parser.OFPFlowMod(dp,
                                    priority = highest_prio,
                                    hard_timeout = timer,
                                    command = ofproto.OFPFC_ADD,
                                    match = match_out,
                                    actions = actions
                                    )
            datapath.send_msg(msg_out)


   
    #Task 3b - check if some users are consuming more traffic
    #        - pool data from switches and drop traffic if
    #        - students exceed 1GB per 1minutes
    #        - professors exceed 5GB per 2minutes    
    @set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
    def _port_stats_reply_handler(self, ev):
        body = ev.msg.body
 
        
        #self.logger.info('datapath         port     '
        #                 'rx-pkts  rx-bytes rx-error '
        #                 'tx-pkts  tx-bytes tx-error')
        #self.logger.info('---------------- -------- '
        #                 '-------- -------- -------- '
        #                 '-------- -------- --------')
        
        for stat in sorted(body, key=attrgetter('port_no')):
            #print(ev.msg.datapath.id, stat.port_no,  stat.rx_bytes,  stat.tx_bytes)
            if (ev.msg.datapath.id, stat.port_no) in self.student_data_counter:
                # Check how much data was transmitted since in last 5seconds
                transmitted_data_in_last_interval = stat.rx_bytes + stat.tx_bytes - self.student_total_data_counter[(ev.msg.datapath.id, stat.port_no)]
                self.student_total_data_counter[(ev.msg.datapath.id, stat.port_no)] = stat.rx_bytes + stat.tx_bytes
                # Add this information to the counter
                self.student_data_counter[(ev.msg.datapath.id, stat.port_no)] += transmitted_data_in_last_interval
                # Check if the usage is under the limit
                if self.student_data_counter[(ev.msg.datapath.id, stat.port_no)] > self.student_data_limit:
                    # Block for the rest of the interval all communication on the corresponding student port
                    hard_rest_timer = self.student_time_limit - (global_timer % self.student_time_limit)
                    mac_dst = self.student_mac_mapping[(ev.msg.datapath.id, stat.port_no)]
                    self.limit_host_traffic_on_sw_port(stat.port_no,ev.msg.datapath,hard_rest_timer,mac_dst)
                    print('Blocking student on switch {} and port {} since consumed data is {}.'.format(ev.msg.datapath.id,stat.port_no,self.student_data_counter[(ev.msg.datapath.id, stat.port_no)]))            
            
            if (ev.msg.datapath.id, stat.port_no) in self.prof_data_counter:
                # Check how much data was transmitted since in last 5seconds
                transmitted_data_in_last_interval = stat.rx_bytes + stat.tx_bytes - self.prof_total_data_counter[(ev.msg.datapath.id, stat.port_no)]
                self.prof_total_data_counter[(ev.msg.datapath.id, stat.port_no)] = stat.rx_bytes + stat.tx_bytes
                # Add this information to the counter
                self.prof_data_counter[(ev.msg.datapath.id, stat.port_no)] += transmitted_data_in_last_interval
                # Check if the usage is under the limit
                if self.prof_data_counter[(ev.msg.datapath.id, stat.port_no)] > self.prof_data_limit:
                    # Block for the rest of the interval all communication on the corresponding prof port
                    mac_dst = self.prof_mac_mapping[(ev.msg.datapath.id, stat.port_no)]
                    hard_rest_timer = self.professor_time_limit - (global_timer % self.professor_time_limit)
                    self.limit_host_traffic_on_sw_port(stat.port_no,ev.msg.datapath,hard_rest_timer,mac_dst)
                    print('Blocking prof on switch {} and port {} since consumed data is {}.'.format(ev.msg.datapath.id,stat.port_no,self.prof_data_counter[(ev.msg.datapath.id, stat.port_no)]))		

            #self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
            #                 ev.msg.datapath.id, stat.port_no,
            #                 stat.rx_packets, stat.rx_bytes, stat.rx_errors,
            #                 stat.tx_packets, stat.tx_bytes, stat.tx_errors)

        #print(self.student_data_counter,self.prof_data_counter)


    #Task 2/3 - Write a function that does:
    #         - Periodically every 5 seconds requests port stats for monitoring
    #         - Block traffic when needed 
    def _monitor(self):
        global global_timer
        global_timer = 0
        
        
        # Wait for the initialization
        hub.sleep(5)
        ssh_port = 22
        http_port = 80

        # Block SSH port and HTTP port on correct switches at the start
        for dp in self.datapaths.values():
            if dp.id in self.student_sw:
                self.block_traffic(http_port,dp)
            if dp.id in self.professor_sw:
                self.block_traffic(ssh_port,dp)
        
        while True:
            #Request data to pool for each switch
            for dp in self.datapaths.values():
    	        self._request_stats(dp)
            hub.sleep(5)
            global_timer = global_timer + 5
            print('Current time is {}'.format(global_timer))
            # Reset counters every 1 min for students and every 2 for professors
            if global_timer % self.student_time_limit == 0:
                self.student_data_counter = {(3,2):0,(3,3):0,(6,2):0,(6,3):0}
                print('Restarting student timers = {}'.format(self.student_data_counter))
            if global_timer % self.professor_time_limit == 0:
                self.prof_data_counter = {(2,2):0,(2,3):0,(5,2):0,(5,3):0}
                print('Restarting prof timers = {}'.format(self.prof_data_counter))
	   
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        #Task 1: Call the function 
	#Use implemented function to check if hosts have permission to communicate
        # Solution 1: Easier solution, uses control plane for checking all packet-ins --> produces a strain/load on controller   
        if not self.check_permission(src,dst):
            return
	# Solution 2: More elegant soultion which doesn't put strain/load on controller --> adds drop rule for pairs of SRC-DST mac pairs..
	
        dpid = datapath.id
        self.mac_to_port.setdefault(dpid, {})

        #self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

        # learn a mac address to avoid FLOOD next time.
        self.mac_to_port[dpid][src] = msg.in_port

        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]

        # install a flow to avoid packet_in next time
        if out_port != ofproto.OFPP_FLOOD:
            self.add_flow(datapath, msg.in_port, dst, actions)

        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath, buffer_id=msg.buffer_id, in_port=msg.in_port,
            actions=actions, data=data)
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
