import socket

def create_client(ip_adress, tcp_port):
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
        PORT = 65432            # The port used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        '''
        socket.AF_INET      -->     IPv4
        socket.SOCK_STREAM  -->     TCP
        '''
        s.connect((HOST, PORT))
        s.sendall(b'Hello, world')
        data = s.recv(1024)

    print('Received', repr(data))


create_client()