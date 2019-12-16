import logging
import threading
import time
from Classes import AppServer, AppClient

# def client_function(name, host, port):
#     logging.info("Client Thread %s: starting", name)
#     (host, port)
#     logging.info("Client Thread %s: finishing", name)

def server_function(name):
    logging.info("Server Thread %s: starting", name)
    AppServer(host, port)
    logging.info("Server Thread %s: finishing", name)

def client_function(name):
    time.sleep(5)
    logging.info("Server Thread %s: starting", name)
    AppClient(host, port, action, value)
    logging.info("Server Thread %s: finishing", name)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    host = ''
    port = 65432
    action = 'search'
    value = 'morpheus'

    logging.info("Main    : before creating thread")
    x = threading.Thread(target=server_function, args=(1,))
    y = threading.Thread(target=client_function, args=(2,))

    logging.info("Main    : before running thread")
    x.start()
    y.start()
    logging.info("Main    : wait for the thread to finish")
    # x.join()
    logging.info("Main    : all done")