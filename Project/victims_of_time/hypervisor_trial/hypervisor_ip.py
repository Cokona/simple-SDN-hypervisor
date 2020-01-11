#from pyof.v0x04.common.utils import unpack_message
#sudo Topo
#sudo mn --custom sdn_topo_2.py --topo mytopo --controller=remote,ip=127.0.0.5,port=65432
#https://stackoverflow.com/questions/20420937/how-to-assign-ip-address-to-interface-in-python
from pyroute2 import IPRoute
#from Project.socket_trials.Classes import AppServer, AppClient
from MultiClasses import MultiClient, MultiServer

host = ''
port = 65432


ip = IPRoute()
index = ip.link_lookup(ifname='lo')[0]
ip.addr('set', index, address='127.0.0.5', mask=24)
print('Starting server')
#AppServer(host, port)
server = MultiServer(host, port)
server.create_server()

print('closed server')
ip.close()
