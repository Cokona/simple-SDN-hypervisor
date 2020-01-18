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

class MyTopo(Topo):
	
	def __init__(self):
		"Create custom topo."
		
		# Initialize topology
		Topo.__init__(self)
		# h1 = self.addHost('h1', ip='10.0.0.1', mac='aa:aa:aa:aa:aa:01') 
		# h2 = self.addHost('h2', ip='20.0.0.2', mac='bb:bb:bb:bb:bb:02')
		# h3 = self.addHost('h3', ip='10.0.0.3', mac='aa:aa:aa:aa:aa:03')
		# h4 = self.addHost('h4', ip='20.0.0.4', mac='bb:bb:bb:bb:bb:04')
		# h5 = self.addHost('h5', ip='10.0.0.5', mac='aa:aa:aa:aa:aa:05')
		# h6 = self.addHost('h6', ip='20.0.0.6', mac='bb:bb:bb:bb:bb:06')
		h1 = self.addHost('h1', ip='10.0.0.1') 
		h2 = self.addHost('h2', ip='20.0.0.2')
		h3 = self.addHost('h3', ip='10.0.0.3')
		h4 = self.addHost('h4', ip='20.0.0.4')
		h5 = self.addHost('h5', ip='10.0.0.5')
		h6 = self.addHost('h6', ip='20.0.0.6')
		
		# Add hosts and switches
		s1 = self.addSwitch('s1')
		s2 = self.addSwitch('s2')
		s3 = self.addSwitch('s3')

		self.addLink(s1, s2)
		self.addLink(s2, s3)

		
		self.addLink(h1, s1)
		self.addLink(h2, s1)
		self.addLink(h3, s2)
		self.addLink(h4, s2)
		self.addLink(h5, s3)
		self.addLink(h6, s3)

topos = {'mytopo': (lambda: MyTopo())}		
	
	
	
	
