import socket
import select
from collections import defaultdict


LOCALHOST = "127.0.0.1"
PORT = 1998 # birth year lol
BUFFER_SIZE_IN_BYTES = 1024
MAX_BUFFER_SIZE_IN_BYTES = 1024*8

# create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# make server socket non blocking to allow concurrent connections
server_socket.setblocking(False)

# bind it to this machine's IP address and a random port number
host_ip_address = socket.gethostname()
server_address = (LOCALHOST, PORT)
server_socket.bind(server_address)


# start listening
server_socket.listen(50)

# lists for select to watch
reads, writes = set([server_socket]), set([])

socket_to_buffer_map = defaultdict(list)
socket_to_response_map = defaultdict(list)

def make_request(buffer):
    request = "".join([bytestr.decode('utf-8') for bytestr in buffer])    
    return request

def build_response(request):
    response = b"HTTP/1.1 200 OK\r\nServer: Hello\r\nContent-Length: 15\r\nContent-Type: text/plain\r\n\r\nHello, Avinash\n"
    return response


# handle recv and send
# try:
while True:

    # print('reads', reads, 'writes', writes)

    ready_for_reads, ready_for_writes, _ = select.select(reads, writes, [])

    for sock in ready_for_reads:
        # print(sock)
        # we have to handle server sockets and client sockets differently
        # in server socket ready for read means new connection available
        if sock is server_socket:
            client_socket, client_address = sock.accept()
            reads.add(client_socket)
        else:
            data = sock.recv(1024)
            socket_to_buffer_map[sock].append(data)
            # when the entire request has been received remove it from reads and put it in writes
            clrf_present = data.find(b"\r\n") > 0
            if clrf_present:
                reads.remove(sock)
                writes.add(sock)
                request = make_request(socket_to_buffer_map[sock])
                socket_to_response_map[sock] = build_response(request)

    for sock in ready_for_writes:
        # print(sock)

        # NOTE: server socket will never be here
        remaining_data_to_send = socket_to_response_map[sock]
        if len(remaining_data_to_send) > 0:
            curr_sent_bytes = sock.send(remaining_data_to_send)
            socket_to_response_map[sock] = remaining_data_to_send[curr_sent_bytes:]

        else:
            writes.remove(sock)
            sock.close()

# except Exception as E:
#     print(E)
#     server_socket.close()
        
