import selectors
import socket
import types

host = '127.0.0.1'
port = 65432

sel = selectors.DefaultSelector()   # Used to select available sockets and stuff???
# ...

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            data.outb += recv_data
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)  # Should be ready to write
            data.outb = data.outb[sent:]



lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((host, port))
lsock.listen()
print('listening on', (host, port))
lsock.setblocking(False)            # To configure the socket in non-blocking mode. 
                                    # Calls made to this socket will no longer block. 
sel.register(lsock, selectors.EVENT_READ, data=None)


while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            # It’s from the listening socket and we need to accept() the connection. 
            # We’ll get the new socket object and register it with the selector. 
            accept_wrapper(key.fileobj)
        else:
            # It’s a client socket that’s already been accepted, and we need to service it. 
            # service_connection() is then called and passed key and mask, which contains everything we need to operate on the socket.
            service_connection(key, mask)


