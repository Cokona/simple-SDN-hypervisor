from mininet.net import Mininet
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def myNet():
    
    #OpenDayLight controller
    ODL_CONTROLLER_IP='10.0.0.4'
    
    print( "*** Creating Null topology")
    net = Mininet( topo=None, build=False)
    
    print( "*** Adding Host h1 to  Null topology name : topo")
    # Create nodes
    h1 = net.addHost( 'h1', mac='01:00:00:00:01:00', ip='192.168.0.1/24' )
    print( "*** Adding Host h2 to  topology topo")
    h2 = net.addHost( 'h2', mac='01:00:00:00:02:00', ip='192.168.0.2/24' )
    
    # Create switches
    print( "*** Adding Switch s1  topology topo: listening port 6634")
    s1 = net.addSwitch( 's1', listenPort=6634, mac='00:00:00:00:00:01' )
    print( "*** Adding Switch s2  topology topo : listening port: 6634")
    s2 = net.addSwitch( 's2', listenPort=6634, mac='00:00:00:00:00:02' )
    print( "*** Creating links")
    print( "*** Creating links h1 s1")
    
    net.addLink(h1, s1, )
    print( "*** Creating links h2 s2")
    net.addLink(h2, s2, )
    print( "*** Creating links s1 s2")
    net.addLink(s1, s2 )
    # Add Controllers
    print( "*** Adding Controller c0 with port 6633")
    odl_ctrl = net.addController( 'c0', controller=RemoteController, ip=ODL_CONTROLLER_IP, port=6633)
    print( "*** Building Network")
    net.build()
    # Connect each switch to a different controller
    print( "*** Starting ODL Controller for switch s1")
    s1.start( [odl_ctrl] )
    s1.cmdPrint('ovs-vsctl show')
    CLI( net )
    net.stop()
    
    if __name__ == '__main__':
        setLogLevel( 'info' )
        myNet()
 
 
 #End of Script
