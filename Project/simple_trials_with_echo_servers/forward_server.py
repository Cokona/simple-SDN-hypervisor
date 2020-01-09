import socket
import select
import logging
import threading
import time
import selectors
import types
from pyof.v0x04.common.utils import unpack_message

connlist = []

def print_packet(binary_packet, source):
    if binary_packet[0] == 4:
        msg = unpack_message(binary_packet)
        # if str(msg.header.message_type) == 'Type.OFPT_HELLO':
        #     print("From " + source + ": OFPT_HELLO")
        #     pass
        # elif str(msg.header.message_type) == 'Type.OFPT_ERROR':
        #     print("From " + source + ': OFPT_ERROR')
        #     pass
        # else:
        print("From " + source +  " : " + str(msg.header.message_type))
    else:
        print("Not an OpenFlow Packet")

def accept_wrapper(sock,sel):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    connlist.append(conn)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ # | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection_server(key, mask,sel,forwarding_socket):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)         # Should be ready to read
        if recv_data:
            data.outb += recv_data           # WE HAVE REMOVED THE +=
            source = "SWITCH"
            print_packet(data.outb,source)
            print("Forwarding message from SWITCH to CONTROLLER")
            sent = forwarding_socket.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
        else:
            #print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
            connlist.remove(sock) 
            print("Socket to SWITCH has been closed")
    
    # if mask & selectors.EVENT_WRITE:
    #     if data.outb:
    #         #print('echoing', repr(data.outb), 'to', data.addr)
    #         print("Forwarding From Server")
    #         sent = forwarding_socket.send(data.outb)  # Should be ready to write
    #         data.outb = data.outb[sent:]

def service_connection_client(key, mask, sel, forwarding_socket):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)         # Should be ready to read
        if recv_data:
            data.outb += recv_data           # WE HAVE REMOVED THE +=
            source = "CONTROLLER"
            print_packet(data.outb,source)
            print("Forwarding message received from CONTROLLER to SWITCH")
            sent = forwarding_socket.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]
        else:
            #print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
            print("Socket to CONTROLLER has been closed")

    # if mask & selectors.EVENT_WRITE:
    #     if data.outb:
    #         #print('echoing', repr(data.outb), 'to', data.addr)
    #         print("Forwarding from server")
    #         sent = forwarding_socket.send(data.outb)  # Should be ready to write
    #         data.outb = data.outb[sent:]



def create_client(ip_address, tcp_port, message=None):
    '''
    Creates a client that sends a TCP connection request to the given ip address and port
        ip_address: string
        tcp_port: integer
    ''' 
    HOST = ip_address
    PORT = tcp_port

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setblocking(False)  
    s.connect_ex((HOST, PORT)) 
    
    print("S has connected to " + str((HOST,PORT)))

    events = selectors.EVENT_READ # | selectors.EVENT_WRITE           
    data = types.SimpleNamespace(addr=s.getsockname(), inb=b'', outb=b'')
    sel.register(s, events, data=data)
    return s

def create_server(sel):
    '''
    Creates a server that listens to TCP connection request in the given ip address and port
        ip_address: string
        tcp_port: integer
    '''
    
    HOST = '127.0.0.1'      # Standard loopback interface address (localhost)
    PORT = 65432              # Port to listen on (non-privileged ports are > 1023)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    s.setblocking(False)
    sel.register(s, selectors.EVENT_READ, data=None)
    
    local_socket = create_client('127.0.0.1', 6633, sel)

    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None and key.fileobj != local_socket:
                accept_wrapper(key.fileobj,sel)

            else:
                if key.fileobj == local_socket:
                    if len(connlist) > 0:
                        # Connection with controller
                        print("1 " + str(connlist))
                        service_connection_client(key, mask, sel, connlist[-1])
                else:
                    # Connection with switches
                    service_connection_server(key, mask, sel,local_socket)

                    



# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
#     logging.info("Main    : before creating thread")
#     server1 = threading.Thread(target=create_server, args=(server1, ))
#     server2 = threading.Thread(target=client_function, args=(2,))

sel = selectors.DefaultSelector()
create_server(sel)