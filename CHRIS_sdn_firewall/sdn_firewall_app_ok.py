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


class SimpleSwitch(app_manager.RyuApp):
	OFP_VERSIONS = [ofproto_v1_0.OFP_VERSION]
	students_mac_list = [   \
		'00:00:00:00:00:03',\
		'00:00:00:00:00:04',\
		'00:00:00:00:00:07',\
		'00:00:00:00:00:08'] 
	professors_mac_list = [ \
		'00:00:00:00:00:01',\
		'00:00:00:00:00:02',\
		'00:00:00:00:00:05',\
		'00:00:00:00:00:06']

	professors_sw_list = [2,5]
	students_sw_list = [3,6]

	def __init__(self, *args, **kwargs):
		super(SimpleSwitch, self).__init__(*args, **kwargs)
		self.mac_to_port = {}
		self.datapaths = {}
		self.data_counter = {}
		self.monitor_thread = hub.spawn(self._monitor)
		self.logger.info('Professors MAC list: %s', SimpleSwitch.professors_mac_list)
		self.logger.info('Students MAC list: %s', SimpleSwitch.students_mac_list)
		self.default_rules_track = []

	#Registring all datapaths for monitor pooling
	@set_ev_cls(ofp_event.EventOFPStateChange,[MAIN_DISPATCHER, DEAD_DISPATCHER])
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
	def _request_stats(self, datapath, port):
		self.logger.debug('send stats request: %016x', datapath.id)
		ofproto = datapath.ofproto
		parser = datapath.ofproto_parser

		# All ports ofproto.OFPP_ALL
		req = parser.OFPPortStatsRequest(datapath, 0, port)
		datapath.send_msg(req)

		#self.logger.info('sent port stats req')


	#Task 1: Write a function which checks if hosts have permission to communicate with each other
	#e.g. you can use MAC addresses of source and destination
	def check_permission(self, l2_src, l2_dst):
		
		if l2_dst == "ff:ff:ff:ff:ff:ff":
			#self.logger.debug('ARP request. Access granted.')
			return True
		elif l2_dst in SimpleSwitch.professors_mac_list and l2_src in SimpleSwitch.professors_mac_list:
			self.logger.info('Professor to professor. Access granted. SRC_MAC: %s DST_MAC: %s', l2_src, l2_dst)
			return True
		elif l2_dst in SimpleSwitch.students_mac_list and l2_src in SimpleSwitch.students_mac_list:
			self.logger.info('Student to student. Access granted. SRC_MAC: %s DST_MAC: %s', l2_src, l2_dst)
			return True
		else:
			#self.logger.info('Access denied. SRC_MAC: %s DST_MAC: %s', l2_src, l2_dst)
			return False

	#Task 2 - Blocking traffic based on TCP port
	#Notes: - add flow rules with higher priority to drop the packets
	#       - take care of timer of flow installation
	#       - for traffic differen
	def block_traffic(self, dst_port, datapath):

		self.logger.info("Blocking %s on %s", dst_port, datapath.id)

		ofproto = datapath.ofproto
		match = datapath.ofproto_parser.OFPMatch(dl_type=2048, nw_proto=6, tp_dst=dst_port)
		mod = datapath.ofproto_parser.OFPFlowMod(
			datapath=datapath, match=match, cookie=0,
			command=ofproto.OFPFC_ADD, idle_timeout=0, hard_timeout=0,
			priority=ofproto.OFP_DEFAULT_PRIORITY,
			flags=ofproto.OFPFF_SEND_FLOW_REM, actions=[])
		datapath.send_msg(mod) 

	#Task 3b - check if some users are consuming more traffic
	#        - pool data from switches and drop traffic if
	#        - students exceed 1GB per 1minutes
	#        - professors exceed 5GB per 2minutes    
	@set_ev_cls(ofp_event.EventOFPPortStatsReply, MAIN_DISPATCHER)
	def _port_stats_reply_handler(self, ev):
		body = ev.msg.body
		dp = ev.msg.datapath.id

		



		#self.logger.info('datapath         port     '
		#				 'rx-pkts  rx-bytes rx-error '
		#				 'tx-pkts  tx-bytes tx-error')
		#self.logger.info('---------------- -------- '
		#				 '-------- -------- -------- '
		#				 '-------- -------- --------')

		for stat in sorted(body, key=attrgetter('port_no')):
			if dp in SimpleSwitch.students_sw_list:
				port = stat.port_no
				traffic = stat.rx_bytes
				self.logger.info('Datapath %s in port %s sent traffic %s', dp, port, traffic)


			#self.logger.info('%016x %8x %8d %8d %8d %8d %8d %8d',
			#				 ev.msg.datapath.id, stat.port_no,
			#				 stat.rx_packets, stat.rx_bytes, stat.rx_errors,
			#				 stat.tx_packets, stat.tx_bytes, stat.tx_errors)


	#Task 2/3 - Write a function that does:
	#         - Periodically every 5 seconds requests port stats for monitoring
	#         - Block traffic when needed 
	def _monitor(self):
		timer = 0
		while True:
			#Request data to pool for each switch
			
			for dp in self.datapaths.values():
				
				#Set up default rules
				if dp.id not in self.default_rules_track:
					if dp.id in SimpleSwitch.professors_sw_list:
						self.block_traffic(22, dp)
						self.default_rules_track.append(dp.id)
					elif dp.id in SimpleSwitch.students_sw_list:
						self.block_traffic(80, dp)
						self.default_rules_track.append(dp.id)
					else:
						# Switch does not have default rule yet
						pass
				#Request stats
				if dp.id in SimpleSwitch.professors_sw_list or dp.id in SimpleSwitch.students_sw_list:
					self._request_stats(dp, 2)
					self._request_stats(dp, 3)

			hub.sleep(5)
			timer = timer + 5

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
		#self.logger.info("%s %s", eth.src, eth.dst)
		is_authorized = self.check_permission(eth.src, eth.dst)
		if is_authorized:

			#self.block_traffic(23, datapath)

			dpid = datapath.id
			self.mac_to_port.setdefault(dpid, {})

			#self.logger.info("packet in %s %s %s %s", dpid, src, dst, msg.in_port)

			#learn a mac address to avoid FLOOD next time.
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
