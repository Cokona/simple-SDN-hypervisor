import selectors
import socket
import types
from time import sleep


num_conns = 1
messages = [b'Message 1 from client.', b'Message 2 from client.']

class MultiClient():
    def __init__(self, host, port, message):
        self.host = host
        self.port = port
        self.message = [message]
        self.sel = selectors.DefaultSelector()   # Used to select available sockets and stuff???

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print('accepted connection from', addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def start_connections(self, host, port, num_conns):
        server_addr = (host, port)
        for i in range(0, num_conns):
            connid = i + 1
            print('starting connection', connid, 'to', server_addr)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            sock.connect_ex(server_addr)
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
            data = types.SimpleNamespace(connid=connid,
                                        msg_total=sum(len(m) for m in self.message),
                                        recv_total=0,
                                        messages=list(self.message),
                                        outb=b'')
            self.sel.register(sock, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                print('received', repr(recv_data), 'from connection', data.connid)
                data.recv_total += len(recv_data)
            # if not recv_data or data.recv_total == data.msg_total:
            #     print('closing connection', data.connid)
            #     self.sel.unregister(sock)
            #     sock.close()
        if mask & selectors.EVENT_WRITE:
            if not data.outb and data.messages:
                data.outb = data.messages.pop(0)
            if data.outb:
                print('sending', repr(data.outb), 'to connection', data.connid)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]

    def create_client(self,cthread,flag):
        self.start_connections(self.host, self.port, num_conns)
        while True:
            cthread.acquire()
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        # It’s from the listening socket and we need to accept() the connection. 
                        # We’ll get the new socket object and register it with the selector. 
                        self.accept_wrapper(key.fileobj)
                    else:
                        # It’s a client socket that’s already been accepted, and we need to service it. 
                        # service_connection() is then called and passed key and mask, which contains everything we need to operate on the socket.
                        self.service_connection(key, mask)
                cthread.notify_all()
            cthread.release()


class MultiServer:
    def __init__(self, host, port, stupid=False):
        self.host = host
        self.port = port
        self.stupid = stupid
        self.sel = selectors.DefaultSelector()   # Used to select available sockets and stuff???
        self.pass_data = None

    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print('accepted connection from', addr)
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)  # Should be ready to read
            if recv_data:
                data.outb += recv_data
            # else:
            #     print('closing connection to', data.addr)
            #     self.sel.unregister(sock)
            #     sock.close()
        if mask & selectors.EVENT_WRITE:
            if data.outb:
                # if not self.stupid:
                #     print('Forwarding')
                #     client = MultiClient(self.host, 6633, data.outb)
                #     client.create_client()
                #     print('Forwarded')
                print('echoing', repr(data.outb), 'to', data.addr)
                sent = sock.send(data.outb)  # Should be ready to write
                data.outb = data.outb[sent:]


    def create_server(self,cthread, flag):
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((self.host, self.port))
        lsock.listen()
        print('listening on', (self.host, self.port))
        lsock.setblocking(False)            # To configure the socket in non-blocking mode. 
                                            # Calls made to this socket will no longer block. 
        self.sel.register(lsock, selectors.EVENT_READ, data=None)

        while True:
            cthread.acquire()
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        # It’s from the listening socket and we need to accept() the connection. 
                        # We’ll get the new socket object and register it with the selector. 
                        self.accept_wrapper(key.fileobj)
                    else:
                        # It’s a client socket that’s already been accepted, and we need to service it. 
                        # service_connection() is then called and passed key and mask, which contains everything we need to operate on the socket.
                        self.service_connection(key, mask)
                cthread.notify_all()
            cthread.release()
