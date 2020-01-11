#from pyof.v0x04.common.utils import unpack_message
#https://stackoverflow.com/questions/20420937/how-to-assign-ip-address-to-interface-in-python
from pyroute2 import IPRoute
#from Project.socket_trials.Classes import AppServer, AppClient
from MultiClasses import MultiClient, MultiServer

host = ''
port = 12345


ip = IPRoute()
index = ip.link_lookup(ifname='lo')[0]
ip.addr('set', index, address='127.0.0.1', mask=24)
print('Starting server')
#AppServer(host, port)
server = MultiServer(host, port, stupid=True)
server.create_server()

print('closed server')
ip.close()
