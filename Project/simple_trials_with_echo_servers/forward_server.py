import socket
import select
import logging
import threading
import time
import selectors
from pyof.v0x04.common.utils import unpack_message

connlist = []

def print_packet(binary_packet, source):
    if binary_packet[0] == 4:
        msg = unpack_message(binary_packet)
        # if str(msg.header.message_type) == 'Type.OFPT_HELLO':
        #     print("From " + str(source) + ": OFPT_HELLO")
        #     pass
        # elif str(msg.header.message_type) == 'Type.OFPT_ERROR':
        #     print("From " + str(source) + ': OFPT_ERROR')
        #     pass
        # else:
        print("From " + str(source) +  " : " + str(msg.header.message_type))
    else:
        print("Not an OpenFlow Packet")

def accept_wrapper(sock,sel):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    connlist.append(conn.dup())
    #data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=None)

def service_connection_server(key, mask,sel,forwarding_socket):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data += recv_data
        else:
            #print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    print_packet(data,str(sock))
        
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            #print('echoing', repr(data.outb), 'to', data.addr)
            print("Forwarding From Server")
            sent = forwarding_socket.send(data.outb)  # Should be ready to write
            data = data[sent:]

def service_connection_client(key, mask, sel, forwarding_socket):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data += recv_data
        else:
            #print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    print_packet(data,str(sock))
        
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            #print('echoing', repr(data.outb), 'to', data.addr)
            print("Forwarding from server")
            sent = forwarding_socket.send(data)  # Should be ready to write
            data = data[sent:]



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
        s.setblocking(False)             
        # s.sendall(message)
        # data = s.recv(1024)
        # s.close()
        #s.set_inheritable(True)
        local_socket = s.dup()
    #print('Received', repr(data))
    return local_socket

def create_server(sel):
    '''
    Creates a server that listens to TCP connection request in the given ip address and port
        ip_address: string
        tcp_port: integer
    '''
    
    
    HOST = '127.0.0.1'      # Standard loopback interface address (localhost)
    PORT = 65434               # Port to listen on (non-privileged ports are > 1023)

    
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    local_socket = create_client('127.0.0.1', 6633)
    #data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    sel.register(local_socket, events, data='')
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # CHECK IF IT WORKS
        s.bind((HOST, PORT))
        s.listen()
        s.setblocking(False)
        sel.register(s, selectors.EVENT_READ, data='')

        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None and key.fileobj != local_socket:
                    accept_wrapper(key.fileobj,sel)
                else:
                    if key.fileobj == local_socket:
                        if len(connlist) > 0:
                            service_connection_client(key, mask, sel, connlist[-1])
                    else:
                        service_connection_server(key, mask, sel,local_socket)

                    



# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
#     logging.info("Main    : before creating thread")
#     server1 = threading.Thread(target=create_server, args=(server1, ))
#     server2 = threading.Thread(target=client_function, args=(2,))

sel = selectors.DefaultSelector()
create_server(sel)