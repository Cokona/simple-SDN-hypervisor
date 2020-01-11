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
        m_p1 = self.addHost('m_p1')  # 10.0.0.5
        m_p2 = self.addHost('m_p2')  # 10.0.0.6
        m_s1 = self.addHost('m_s1')  # 10.0.0.7
        m_s2 = self.addHost('m_s2')  # 10.0.0.8

        g_p1 = self.addHost('g_p1')  # 10.0.0.1
        g_p2 = self.addHost('g_p2')  # 10.0.0.2
        g_s1 = self.addHost('g_s1')  # 10.0.0.3
        g_s2 = self.addHost('g_s2')  # 10.0.0.4

        munich = self.addSwitch('s1')

        munich_prof = self.addSwitch('s2')
        munich_stud = self.addSwitch('s3')

        garching = self.addSwitch('s4')

        garching_prof = self.addSwitch('s5')
        garching_stud = self.addSwitch('s6')

        ixp1 = self.addSwitch('s11')
        ixp2 = self.addSwitch('s12')
        ixp3 = self.addSwitch('s13')

        # backbone links
        self.addLink(munich, ixp1)
        self.addLink(munich, ixp2)
        self.addLink(munich, ixp3)
        self.addLink(ixp1, garching)
        self.addLink(ixp2, garching)
        self.addLink(ixp3, garching)

        # links between switches in garching
        self.addLink(garching, garching_prof)
        self.addLink(garching, garching_stud)
        # links between switches in munich
        self.addLink(munich, munich_prof)
        self.addLink(munich, munich_stud)

        # links between hosts and switches
        self.addLink(m_p1, munich_prof)
        self.addLink(m_p2, munich_prof)
        self.addLink(m_s1, munich_stud)
        self.addLink(m_s2, munich_stud)
        self.addLink(g_p1, garching_prof)
        self.addLink(g_p2, garching_prof)
        self.addLink(g_s1, garching_stud)
        self.addLink(g_s2, garching_stud)


topos = {'mytopo': (lambda: MyTopo())}
