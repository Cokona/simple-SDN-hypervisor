
#https://stackoverflow.com/questions/17774768/python-creating-a-shared-variable-between-threads
import logging
import threading
import time
from pyroute2 import IPRoute
#from Project.socket_trials.Classes import AppServer, AppClient
from MultiClasses import MultiClient, MultiServer


# def client_function(name, host, port):
#     logging.info("Client Thread %s: starting", name)
#     (host, port)
#     logging.info("Client Thread %s: finishing", name)

c = threading.Condition()
upwards = 'DOooooo'
downwards = None
flag = 1

def server_function(name):
    global upwards
    global downwards
    global flag

    logging.info("Server Thread %s: starting", name)
    # Copied from hypervisor IP
    host = ''
    port = 65432
    ip = IPRoute()
    index = ip.link_lookup(ifname='lo')[0]
    ip.addr('set', index, address='127.0.0.5', mask=24)
    print('Starting server')
    #AppServer(host, port)
    server = MultiServer(host, port)
    server.create_server(c,flag)
    print('closed server')
    ip.close()
    logging.info("Server Thread %s: finishing", name)

def client_function(name):
    global upwards
    global downwards
    global flag

    logging.info("Server Thread %s: starting", name)
    client = MultiClient('127.0.0.1', 6633, upwards)
    client.create_client(c,flag)
    logging.info("Server Thread %s: finishing", name)
    

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

   
    logging.info("Main    : before creating thread")
    x = threading.Thread(target=server_function, args=(1,))
    y = threading.Thread(target=client_function, args=(2,))

    logging.info("Main    : before running thread")
    x.start()
    y.start()
    logging.info("Main    : wait for the thread to finish")
    # x.join()
    logging.info("Main    : all done")