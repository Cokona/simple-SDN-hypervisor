import socket
import logging
import threading
import time

def create_client(ip_address, tcp_port, message=None, conn_client=None, addr_client=None):
    '''
    Creates a client that sends a TCP connection request to the given ip address and port
        ip_address: string
        tcp_port: integer
    '''
    if not conn_client:
        print('Client establishing new connection with ryu')
        HOST = ip_address
        PORT = tcp_port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            conn, addr = s.getsockname()
            s.sendall(message)
            data = s.recv(1024)
            return data, conn, addr
    else:
        print('Client re-establishing old connection with ryu')
        HOST = conn_client
        PORT = addr_client
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.sendall(message)
            data = s.recv(1024)
            return data
    # print('Received', repr(data))


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
        PORT = 65434                # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        while True:
            conn_client, addr_client = None, None
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    # print('Data received ' + str(data))
                    if not data:
                        break
                    ryu_reaction_data, conn_client, addr_client = create_client(ip_address='127.0.0.1', tcp_port=6633, message=data, conn_client=conn_client, addr_client=addr_client)
                    conn.sendall(ryu_reaction_data)
                    # print('Message has been forwarded')



# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
#     logging.info("Main    : before creating thread")
#     server1 = threading.Thread(target=create_server, args=(server1, ))
#     server2 = threading.Thread(target=client_function, args=(2,))


create_server()
