"""Custom topology 

- s1 - s2 
  |     |
 h1     h2
 

h1, h3, h5 --> c1
h2, h4, h6 --> c2

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.link import TCLink
from mininet.topo import Topo

class MyTopo(Topo):
	
	def __init__(self):
		"Create custom topo."
		
		# Initialize topology
		Topo.__init__(self)
		h1 = self.addHost('h1', ip='10.0.0.1', mac='aa:aa:aa:aa:aa:01') 
		h2 = self.addHost('h2', ip='10.0.0.2', mac='aa:aa:aa:aa:aa:02')

		# Add hosts and switches
		s1 = self.addSwitch('s1')
		s2 = self.addSwitch('s2')

		self.addLink(s1, s2)
		
		self.addLink(h1, s1)
		self.addLink(h2, s2)
		
topos = {'mytopo': (lambda: MyTopo())}		
	
	
	
	
