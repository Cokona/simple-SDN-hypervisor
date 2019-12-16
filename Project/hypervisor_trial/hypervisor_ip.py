#from pyof.v0x04.common.utils import unpack_message
#https://stackoverflow.com/questions/20420937/how-to-assign-ip-address-to-interface-in-python
from pyroute2 import IPRoute
ip = IPRoute()
index = ip.link_lookup(ifname='lo')[0]
ip.addr('set', index, address='192.168.0.1', mask=24)
ip.close()
