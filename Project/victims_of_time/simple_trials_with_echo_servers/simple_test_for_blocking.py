import socket

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
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    data = conn.recv(1024)
                    print('Data received ' + str(data))
                    if not data:
                        break

create_server()