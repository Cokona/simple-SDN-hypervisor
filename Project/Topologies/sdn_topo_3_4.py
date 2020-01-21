"""Custom topology 

 -s1 ----- s2 -----s3-
  | |     | |     | |  
 h1 h2   h3 h4   h5 h6
 

h1, h3, h5 --> c1
h2, h4, h6 --> c2

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.link import TCLink
from mininet.topo import Topo
import string

class MyTopo(Topo):
	
	def __init__(self):
		"Create custom topo."
		
		no_of_slices = 3
		no_of_switches = 4
		switch_dict = {}
		host_dict = {}
		for ind_sl in range(no_of_slices):
			host_dict[ind_sl] = {}

		# Initialize topology
		Topo.__init__(self)

		for ind_sw in range(no_of_switches):
			switch_name = 's'+str(ind_sw+1)
			switch_dict[switch_name] = self.addSwitch(switch_name)
			if ind_sw > 0:
				prev_switch_name = 's'+str(ind_sw)
				self.addLink(switch_dict[prev_switch_name],switch_dict[switch_name])

			for ind_sl in range(no_of_slices):
				host_name = 'h'+str(ind_sl+1)+'_'+str(ind_sw+1)
				ip = str(ind_sl+1) + '0.0.0.' + str(ind_sw+1)
				# mac = string.ascii_lowercase[2*ind_sl] + string.ascii_lowercase[2*ind_sl] +':'
				# mac = mac+mac+mac+mac+mac+'0' + str(ind_sw+1)
				host_dict[ind_sl][host_name] = self.addHost(host_name, ip=ip) 
				self.addLink(host_dict[ind_sl][host_name],switch_dict[switch_name])


topos = {'mytopo': (lambda: MyTopo())}		
	
	
	
	
