import socket
import logging
import threading
import time

def create_client(ip_address, tcp_port, message=None):
    '''
    Creates a client that sends a TCP connection request to the given ip address and port
        ip_address: string
        tcp_port: integer
    '''
    HOST = ip_address
    PORT = tcp_port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        '''
        socket.AF_INET      -->     IPv4
        socket.SOCK_STREAM  -->     TCP
        '''
        s.connect((HOST, PORT))
        s.sendall(message)
        data = s.recv(1024)
        # print('Received', repr(data))
    return data

def create_server(ip_address=None, tcp_port=None):
    '''
    Creates a server that listens to TCP connection request in the given ip address and port
        ip_address: string
        tcp_port: integer
    '''
    if ip_address and tcp_port:
        HOST = ip_address
        PORT = tcp_port
    else:
        HOST = '127.0.0.1'      # Standard loopback interface address (localhost)
        PORT = 65433                # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        while True:
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    # print('Data received ' + str(data))
                    if not data:
                        break
                    ryu_reaction_data = create_client(ip_address='127.0.0.1', tcp_port=6633, message=data)
                    conn.sendall(ryu_reaction_data)
                    # print('Message has been forwarded')



# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
#     logging.info("Main    : before creating thread")
#     server1 = threading.Thread(target=create_server, args=(server1, ))
#     server2 = threading.Thread(target=client_function, args=(2,))

# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")

#     host = ''
#     port = 65432
#     action = 'search'
#     value = 'morpheus'

#     logging.info("Main    : before creating thread")
#     x = threading.Thread(target=server_function, args=(1,))
#     y = threading.Thread(target=client_function, args=(2,))

#     logging.info("Main    : before running thread")
#     x.start()
#     y.start()
#     logging.info("Main    : wait for the thread to finish")
#     # x.join()
#     logging.info("Main    : all done")



create_server()
