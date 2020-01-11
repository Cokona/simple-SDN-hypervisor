import socket

def create_client(ip_address='127.0.0.1', tcp_port=65430, message=b'Hello World'):
    '''
    Creates a client that sends a TCP connection request to the given ip address and port
        ip_address: string
        tcp_port: integer
    '''
    if ip_address or tcp_port:
        HOST = ip_address
        PORT = tcp_port
    else:
        HOST = '127.0.0.1'      # The server's hostname or IP address
        PORT = 65430            # The port used by the server

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


create_client()