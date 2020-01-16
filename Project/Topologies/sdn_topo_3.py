"""Custom topology 

 	 -s1-
  | |   | |  
 h1 h2 h3 h4
 

h1, h3 --> c1
h2, h4 --> c2

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
		h2 = self.addHost('h2', ip='20.0.0.2', mac='bb:bb:bb:bb:bb:02')
		h3 = self.addHost('h3', ip='10.0.0.3', mac='aa:aa:aa:aa:aa:03')
		h4 = self.addHost('h4', ip='20.0.0.4', mac='bb:bb:bb:bb:bb:04')
		
		# Add hosts and switches
		s1 = self.addSwitch('s1')

		self.addLink(h1, s1)
		self.addLink(h2, s1)
		self.addLink(h3, s1)
		self.addLink(h4, s1)

topos = {'mytopo': (lambda: MyTopo())}		
	
	
	
	
