import socket
import select
import logging
import threading
import time
import selectors
from pyof.v0x04.common.utils import unpack_message

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
        
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # CHECK IF IT WORKS
        #local_socket = s.create_connection((HOST, PORT))
        s.connect((HOST, PORT)) 
        s.setblocking(1)             
        # s.sendall(message)
        # data = s.recv(1024)
        # s.close()
        #s.set_inheritable(True)
        local_socket = s.dup()
    #print('Received', repr(data))
    return local_socket

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
        PORT = 65434               # Port to listen on (non-privileged ports are > 1023)
    
    local_socket = create_client('127.0.0.1', 6633)
    #ready = select.select([local_socket], [], [], 10)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # CHECK IF IT WORKS
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
                    #print('Received from Switch', repr(data))
                    binary_msg = data
                    
                    if binary_msg[0] == 4:
                        msg = unpack_message(binary_msg)
                        if str(msg.header.message_type) == 'Type.OFPT_HELLO':
                            print("From Switch: OFPT_HELLO")
                            pass
                        elif str(msg.header.message_type) == 'Type.OFPT_ERROR':
                            print("From Switch: OFPT_ERROR")
                            pass
                        else:
                            print('From Switch: ' + str(msg.header.message_type))
                            pass
                    else:
                        print("Not an Openflow Packet")

                    # HERE INSERT CODE FOR OPENED CLIENT SOCKET
                    local_socket.sendall(data)
                    
                    ryu_reaction_data = local_socket.recv(1024)

                    binary_msg1 = ryu_reaction_data
                    #print('Received from Ryu', repr(ryu_reaction_data))
                    if binary_msg1[0] == 4:
                        msg = unpack_message(binary_msg1)
                        if str(msg.header.message_type) == 'Type.OFPT_HELLO':
                            print("From Controller: OFPT_HELLO")
                            pass
                        elif str(msg.header.message_type) == 'Type.OFPT_ERROR':
                            print("From Controller: OFPT_ERROR")
                            pass
                        else:
                            print("From Controller" + str(msg.header.message_type))
                            pass
                    else:
                        print("Not an OpenFlow Packet")
                    #print('Message has been forwarded')
                    conn.sendall(ryu_reaction_data)



# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
#     logging.info("Main    : before creating thread")
#     server1 = threading.Thread(target=create_server, args=(server1, ))
#     server2 = threading.Thread(target=client_function, args=(2,))


create_server()
