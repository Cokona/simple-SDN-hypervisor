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
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_0
from ryu.lib.mac import haddr_to_bin
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from ryu.lib.packet import tcp
from ryu.lib import hub

macDict = {'p': {'m_p1':'00:00:00:00:00:05', 'm_p2':'00:00:00:00:00:06','g_p1':'00:00:00:00:00:01','g_p2':'00:00:00:00:00:02'},
's':{'m_s1':'00:00:00:00:00:07','m_s2':'00:00:00:00:00:08','g_s1':'00:00:00:00:00:03','g_s2':'00:00:00:00:00:04'}}

class SimpleSwitch(app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]

	def __init__(self, *args, **kwargs):
		super(SimpleSwitch, self).__init__(*args, **kwargs)
		self.mac_to_port = {}
		self.datapaths = {}
		self.data_counter = {}
		self.monitor_thread = hub.spawn(self._monitor)


	# Registring all datapaths for monitor pooling
	@set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
	def _state_change_handler(self, ev):
		datapath = ev.datapath
		if ev.state == MAIN_DISPATCHER:
			if datapath.id not in self.datapaths:
				self.logger.debug('register datapath: %016x', datapath.id)
				self.datapaths[datapath.id] = datapath
				self.data_counter[datapath.id] = 0
		elif ev.state == DEAD_DISPATCHER:
			if datapath.id in self.datapaths:
				self.logger.debug('unregister datapath: %016x', datapath.id)
				del self.datapaths[datapath.id]
				del self.data_counter[datapath.id]

	def add_flow(self, datapath, in_port, dst, actions, priority=0, tcp_port=None):
		ofproto = datapath.ofproto

		match = datapath.ofproto_parser.OFPMatch(
			in_port=in_port, dl_dst=haddr_to_bin(dst), tp_dst=tcp_port)

		mod = datapath.ofproto_parser.OFPFlowMod(
			datapath=datapath, match=match, cookie=0,
			command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
			priority=ofproto.OFP_DEFAULT_PRIORITY + priority,
			flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions, )
		
		#self.logger.info(ofproto.OFP_DEFAULT_PRIORITY+priority)

		datapath.send_msg(mod)

	# Task 3a: Requesting port stats for a specific datapath
	# def _request_stats(self, datapath):
	#    self.logger.debug('send stats request: %016x', datapath.id)
	#
	#    datapath.send_msg(req)
	#    #self.logger.info('sent port stats req')

	# Task 1: Write a function which checks if hosts have permission to communicate with each other
	# e.g. you can use MAC addresses of source and destination
	def check_permission(self, mac_src, mac_dst):
		# If my src is an s and my dst is a p, it will return FALSE --> meaning no 	
		return not ((mac_src in macDict['s'].values() and mac_dst in macDict['p'].values() ) or (
			 		mac_src in macDict['p'].values() and mac_dst in macDict['s'].values()))


	# Task 2 - Blocking traffic based on TCP port
	# Notes: - add flow rules with higher priority to drop the packets
	#       - take care of timer of flow installation
	#       - for traffic differen
	def block_traffic(self, datapath, port, dl_dst):
		self.logger.info("Blocking port %s on switch %s", port, datapath.id)

		ofproto = datapath.ofproto
		match = datapath.ofproto_parser.OFPMatch(dl_type=0x0800, nw_proto=6, tp_dst=port, dl_dst=haddr_to_bin(dl_dst))
		actions = [datapath.ofproto_parser.OFPActionOutput(ofproto.OFPPC_NO_FWD)]
		mod = datapath.ofproto_parser.OFPFlowMod(
			datapath=datapath, match=match, cookie=0,
			command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
			priority=ofproto.OFP_DEFAULT_PRIORITY+5,
			flags=ofproto.OFPFF_SEND_FLOW_REM, actions=actions)
		datapath.send_msg(mod) 



	# Task 3b - check if some users are consuming more traffic
	#        - pool data from switches and drop traffic if
	#        - students exceed 1GB per 1minutes
	#        - professors exceed 5GB per 2minutes
	@set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
	def _port_stats_reply_handler(self, ev):
		body = ev.msg.body

		self.logger.info('datapath         port     '
						'rx-pkts  rx-bytes rx-error '
						'tx-pkts  tx-bytes tx-error')
		self.logger.info('---------------- -------- '
						'-------- -------- -------- '
						'-------- -------- --------')

		for stat in sorted(body, key=attrgetter('port_no')):
			self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
							ev.msg.datapath.id, stat.port_no,
							stat.rx_packets, stat.rx_bytes, stat.rx_errors,
							stat.tx_packets, stat.tx_bytes, stat.tx_errors)

	# Task 2/3 - Write a function that does:
	#         - Periodically every 5 seconds requests port stats for monitoring
	#         - Block traffic when needed
	def _monitor(self):
		timer = 0
		while True:
			# Request data to pool for each switch
			# for dp in self.datapaths.values():
			# 	self._request_stats(dp)
			
			hub.sleep(5)
			timer = timer + 5

	@set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
	def _packet_in_handler(self, ev):
		msg = ev.msg
		datapath = msg.datapath
		ofproto = datapath.ofproto

		pkt = packet.Packet(msg.data)
		eth = pkt.get_protocol(ethernet.ethernet)
		
		if pkt.get_protocol(tcp.tcp):
			tp = pkt.get_protocol(tcp.tcp)
			# self.logger.info(tp.dst_port)
		else:
			tp = None

		if eth.ethertype == ether_types.ETH_TYPE_LLDP:
			# ignore lldp packet
			return
		dst = eth.dst
		src = eth.src
		
	# Task 1: Call the function
		if not self.check_permission(src,dst):
			self.logger.info('Permission Denied')
			out_port = ofproto.OFPPC_NO_FWD
			actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
			self.add_flow(datapath, msg.in_port, dst, actions)
	
	# IF WE HAVE TIME LATER:
	# Implement the code to let ARP messages go through but not IP messages
		# Use implemented function to check if hosts have permission to communicate
		else: # Permission Granted from Task 1:
			dpid = datapath.id
			self.mac_to_port.setdefault(dpid, {})
			
			## TASK 2 - Proactive TCP port block
			if dst in macDict['s'].values():
				self.block_traffic(datapath, port=80, dl_dst=dst)
			elif dst in macDict['p'].values():
				self.block_traffic(datapath, port=22, dl_dst=dst)
			###################
		    # Permission granted form Task 2
			# self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

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
