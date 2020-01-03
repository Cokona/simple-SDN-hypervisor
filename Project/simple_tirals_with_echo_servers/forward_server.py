import socket

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
        # data = s.recv(1024)

    # print('Received', repr(data))
    print('Message sent from client')

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
        HOST = '127.0.0.1'       # Standard loopback interface address (localhost)
        PORT = 65432         # Port to listen on (non-privileged ports are > 1023)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                if data:
                    create_client(ip_address='127.0.0.1', tcp_port=6633, message=data)
                    print('Message has been forwarded')

create_server()