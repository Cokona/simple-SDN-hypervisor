from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSKernelSwitch, UserSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink


def topology():

        # net = Mininet( controller=RemoteController, link=TCLink, switch=OVSKernelSwitch )
        net = Mininet( controller=RemoteController, link=TCLink, switch=OVSKernelSwitch)

        # Add hosts and switches
        h1 = net.addHost('h1', ip="192.168.0.1", defaultRoute='via 192.168.0.254')
        h2 = net.addHost('h2', ip="192.168.0.2", defaultRoute='via 192.168.0.254')
        h3 = net.addHost('h3', ip="10.0.0.1", defaultRoute='via 10.0.0.254')

        s1 = net.addSwitch( 's1')
        c0 = net.addController( 'c0') #, controller=RemoteController, ip='127.0.0.1', port=6633 )

        net.addLink( h1, s1 , port=1)
        net.addLink( h2, s1 , port=2)
        net.addLink( h3, s1 , port=3)
        net.build()

        c0.start()
        s1.start( [c0] )
                
        h1.cmd("arp -s 192.168.0.254 00:00:00:00:11:11")
        h2.cmd("arp -s 192.168.0.254 00:00:00:00:11:11")
        h3.cmd("arp -s 10.0.0.254 00:00:00:00:33:33")

        print( "*** Running CLI")
        CLI( net )

        print("*** Stopping network")
        net.stop()


if __name__ == '__main__':

    setLogLevel( 'info' )
    topology()  