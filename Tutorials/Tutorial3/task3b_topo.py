"""Custom topology example

Two directly connected switches plus a host for each switch:

look at the github topop

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.link import TCLink

class MyTopo(Topo):
    "Simple topology example."

    def __init__(self):
        "Create custom topo."

        # Initialize topology
        Topo.__init__(self)

        # Add hosts and switches
        h1 = self.addHost('h1', ip="192.168.0.1", defaultRoute='via 192.168.0.254')
        h2 = self.addHost('h2', ip="192.168.0.2", defaultRoute='via 192.168.0.254')
        h3 = self.addHost('h3', ip="10.0.0.1", defaultRoute='via 10.0.0.254')
        
        # h1.cmd("arp -s 192.168.0.254 00:00:00:00:11:11")
        # h2.cmd("arp -s 192.168.0.254 00:00:00:00:11:11")
        # h3.cmd("arp -s 10.0.0.254 00:00:00:00:33:33")

        s1 = self.addSwitch('s1')

        # links between hosts and switches
        self.addLink(h1, s1)
        self.addLink(h2, s1)
        self.addLink(h3, s1)


topos = {'mytopo': (lambda: MyTopo())}
