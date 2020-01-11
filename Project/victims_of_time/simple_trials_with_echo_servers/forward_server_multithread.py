import socket
import logging
import threading
import time
from pyof.v0x04.common.utils import unpack_message

event_send_data = threading.Event()
event_reaction_received = threading.Event()
message_to_send = None
ryu_reaction_data = None
ryu_async = None


def create_client(ip_address, tcp_port):
    '''
    Creates a client that sends a TCP connection request to the given ip address and port
        ip_address: string
        tcp_port: integer
    '''

    global message_to_send
    global ryu_reaction_data
    global ryu_async

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        '''
        socket.AF_INET      -->     IPv4
        socket.SOCK_STREAM  -->     TCP
        '''
        s.connect((ip_address, tcp_port))

        while True:
            if event_send_data.is_set():
                s.sendall(message_to_send)
                # print('I am stuck before ryu_reaction_data')
                ryu_reaction_data = s.recv(1024)
                # print('RYU_REACT has been reset')
                event_send_data.clear()
                event_reaction_received.set()
    #print('Received', repr(data))

def create_server(ip_address, tcp_port):
    '''
    Creates a server that listens to TCP connection request in the given ip address and port
        ip_address: string
        tcp_port: integer
    '''
    global message_to_send
    global ryu_reaction_data

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)         # CHECK IF IT WORKS
        s.bind((ip_address, tcp_port))
        while True:
            s.listen()
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                while True:
                    # print('I am stuck before conn.recv')
                    data = conn.recv(1024)
                    # print('Data received ' + str(data))
                    if not data:
                        break
                    #print('Received from Switch', repr(data))
                    binary_msg = data
                    print(binary_msg[0])
                    if binary_msg[0] == 4:
                        msg = unpack_message(binary_msg)
                        # if str(msg.header.message_type) == 'Type.OFPT_HELLO':
                        #     print("From Switch: OFPT_HELLO")
                        # elif str(msg.header.message_type) == 'Type.OFPT_ERROR':
                        #     print("From Switch: OFPT_ERROR")
                        #     pass
                        # else:
                        #     print('From Switch: ' + str(msg.header.message_type))
                        print('From Switch: ' + str(msg.header.message_type) + '  SIZE: ' + str(len(data)))

                    ####### IMPLEMENT SHARED MEMORY SHIT #############  
                    message_to_send = data
                    event_send_data.set()
                    # print('I am stuck before event.wait()')
                    event_reaction_received.wait()
                    event_reaction_received.clear()


                    #print('Received from Ryu', repr(ryu_reaction_data))
                    binary_msg = ryu_reaction_data

                    print(binary_msg[0])
                    if binary_msg[0] == 4:
                        msg = unpack_message(binary_msg)
                        # if str(msg.header.message_type) == 'Type.OFPT_HELLO':
                        #     print("From Controller: OFPT_HELLO")
                        #     pass
                        # elif str(msg.header.message_type) == 'Type.OFPT_ERROR':
                        #     print("From Controller: OFPT_ERROR")
                        # else:
                        #     print("From Controller" + str(msg.header.message_type))
                        print("From Controller" + str(msg.header.message_type) + '  SIZE: ' + str(len(data)))
                    conn.sendall(ryu_reaction_data)
                    #print('Message has been forwarded')



if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.info("Main    : before creating thread")
    server_switch = threading.Thread(target=create_server, args=('127.0.0.1', 65432))
    server_switch.start()
    logging.info("Main    : Server Created")

    client_controller = threading.Thread(target=create_client, args=('127.0.0.1', 6633))
    client_controller.start()
    logging.info("Main    : Client Created")


# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
#     logging.info("Main    : before creating thread")
#     server1 = threading.Thread(target=create_server, args=(server1, ))
#     server2 = threading.Thread(target=client_function, args=(2,))

# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.INFO,
#                         datefmt="%H:%M:%S")

#     host = ''
#     port = 65432
#     action = 'search'
#     value = 'morpheus'

#     logging.info("Main    : before creating thread")
#     x = threading.Thread(target=server_function, args=(1,))
#     y = threading.Thread(target=client_function, args=(2,))

#     logging.info("Main    : before running thread")
#     x.start()
#     y.start()
#     logging.info("Main    : wait for the thread to finish")
#     # x.join()
#     logging.info("Main    : all done")