import socket


LOCALHOST = "127.0.0.1"
PORT = 1998 # birth year lol
BUFFER_SIZE_IN_BYTES = 1024
MAX_BUFFER_SIZE_IN_BYTES = 1024*8

def receive_request(client_socket, buffer_size=BUFFER_SIZE_IN_BYTES, max_buffer_size=MAX_BUFFER_SIZE_IN_BYTES):
    # blocking sequential socket
    num_bytes_received = 0
    buffer = []
    while num_bytes_received < MAX_BUFFER_SIZE_IN_BYTES:
        data = client_socket.recv(1024)
        num_bytes_received += len(data)
        buffer.append(data)
        clrf_present = data.find(b"\r\n") > 0
        if clrf_present: break
    request = "".join([bytestr.decode('utf-8') for bytestr in buffer])    
    return request

def send_response(client_socket):
    response = b"HTTP/1.1 200 OK\r\nServer: Hello\r\nContent-Length: 13\r\nContent-Type: text/plain\r\n\r\nHello, world\n"
    num_bytes_sent = 0
    while num_bytes_sent < len(response):
        curr_sent_bytes = client_socket.send(response[num_bytes_sent:])
        num_bytes_sent += curr_sent_bytes

# create a socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind it to this machine's IP address and a random port number
host_ip_address = socket.gethostname()
server_address = (LOCALHOST, PORT)
server_socket.bind(server_address)

# start listening
server_socket.listen(5)

# handle recv and send
while True:
    client_socket, client_address = server_socket.accept()
    request = receive_request(client_socket)
    send_response(client_socket)
    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()

