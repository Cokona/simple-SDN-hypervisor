# #!/usr/bin/env python3

import sys
import socket
import selectors
import traceback

import libserver
import libclient

class AppServer:
    def __init__(self, host, port):
        self.sel = selectors.DefaultSelector()
        self.host = host
        self.port = port
        self.lsock = None

        self.set_sockets()
        self.start_server()

    def set_sockets(self):
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Avoid bind() exception: OSError: [Errno 48] Address already in use
        self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.lsock.bind((self.host, self.port))
        self.lsock.listen()
        print("listening on", (self.host, self.port))
        self.lsock.setblocking(False)
        self.sel.register(self.lsock, selectors.EVENT_READ, data=None)
    
    def accept_wrapper(self, sock):
        conn, addr = sock.accept()  # Should be ready to read
        print("accepted connection from", addr)
        conn.setblocking(False)
        message = libserver.Message(self.sel, conn, addr)
        self.sel.register(conn, selectors.EVENT_READ, data=message)

    def start_server(self):
        try:
            while True:
                events = self.sel.select(timeout=None)
                for key, mask in events:
                    if key.data is None:
                        self.accept_wrapper(key.fileobj)
                    else:
                        message = key.data
                        try:
                            message.process_events(mask)
                        except Exception:
                            print(
                                "main: error: exception for",
                                f"{message.addr}:\n{traceback.format_exc()}",
                            )
                            message.close()
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()


class AppClient:
    def __init__(self, host, port, action, value):
        self.sel = selectors.DefaultSelector()
        self.host = host
        self.port = port
        self.action = action
        self.value = value
        self.request = None
        self.addr = None
        self.sock = None

        self.start_client()
        

    def create_request(self, action, value):
        if action == "search":
            return dict(
                type="text/json",
                encoding="utf-8",
                content=dict(action=action, value=value),
            )
        else:
            return dict(
                type="binary/custom-client-binary-type",
                encoding="binary",
                content=bytes(action + value, encoding="utf-8"),
            )


    def start_connection(self, host, port, request):
        self.addr = (self.host, self.port)
        print("starting connection to", self.addr)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setblocking(False)
        self.sock.connect_ex(self.addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        message = libclient.Message(self.sel, self.sock, self.addr, self.request)
        self.sel.register(self.sock, events, data=message)

    def start_client(self):
        self.request = self.create_request(self.action, self.value)
        self.start_connection(self.host, self.port, self.request)

        try:
            while True:
                events = self.sel.select(timeout=1)
                for key, mask in events:
                    message = key.data
                    try:
                        message.process_events(mask)
                    except Exception:
                        print(
                            "main: error: exception for",
                            f"{message.addr}:\n{traceback.format_exc()}",
                        )
                        message.close()
                # Check for a socket being monitored to continue.
                if not self.sel.get_map():
                    break
        except KeyboardInterrupt:
            print("caught keyboard interrupt, exiting")
        finally:
            self.sel.close()