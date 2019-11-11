"""Custom topology example

Two directly connected switches plus a host for each switch:

look at the github topop

Adding the 'topos' dict with a key/value pair to generate our newly defined
topology enables one to pass in '--topo=mytopo' from the command line.
"""

from mininet.topo import Topo
from mininet.link import TCLink

class MyTopo( Topo ):
    "Simple topology example."

    def __init__( self ):
        "Create custom topo."

        # Initialize topology
        Topo.__init__( self )

        # Add hosts and switches
        m_p1 = self.addHost( 'm_p1' )
        m_p2 = self.addHost( 'm_p2' )
        m_s1 = self.addHost( 'm_s1' )
        m_s2 = self.addHost( 'm_s2' )
        
        g_p1 = self.addHost( 'g_p1' )
        g_p2 = self.addHost( 'g_p2' )
        g_s1 = self.addHost( 'g_s1' )
        g_s2 = self.addHost( 'g_s2' )
        

             
        munich = self.addSwitch('s1')
    
        munich_prof = self.addSwitch( 's2' )
        munich_stud = self.addSwitch( 's3' )
        
        garching = self.addSwitch( 's4' )
        garching_prof = self.addSwitch( 's5' )
        garching_stud = self.addSwitch( 's6' )
        
        #backbone link
        self.addLink(munich,garching,bw=10000)
        #links between switches in garching
        self.addLink(garching,garching_prof,bw=1000)
        self.addLink(garching,garching_stud,bw=1000)
        #links between switches in munich
        self.addLink(munich,munich_prof,bw=1000)
        self.addLink(munich,munich_stud,bw=1000)
        
        #links between hosts and switches
        self.addLink(m_p1,munich_prof)
        self.addLink(m_p2,munich_prof)
        self.addLink(m_s1,munich_stud)
        self.addLink(m_s2,munich_stud)
        self.addLink(g_p1,garching_prof)
        self.addLink(g_p2,garching_prof)
        self.addLink(g_s1,garching_stud)
        self.addLink(g_s2,garching_stud)
              
topos = { 'mytopo': ( lambda: MyTopo() ) }

