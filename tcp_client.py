# tcp_client.py
# Cloud-Server Project for Computer Networks

"""
Server-Client Architecture: Implement server-client where clients initiate connections
to central server for file requests and transfers
"""

import socket

# client and server should match port
host = '127.0.0.1'
port = 3300

BUFFER_SIZE = 1024

# Client function sends file to server
def file_send(client_tcp, filename):
    try:
        with open(filename, 'r') as fi:
            data = fi.read()
            while data:
                client_tcp.send(data.encode())
                data = fi.read()

        print(f'[*] File {filename} was sent successfully')
    except IOError:
        print('Error: File not found. Please provide valid filename.')


# Client Setup
if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
        client_tcp.connect((host, port))
        print('[*] Connected to server')  # at {host}:{port}

        while True:
            filename = input('Input filename you want to send (or "q" to quit): ')
            if filename.lower() == 'q':
                break
            file_send(client_tcp, filename)

