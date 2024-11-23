# tcp_server.py
# Cloud-Server Project for Computer Networks

"""
Server-Client Architecture: Implement server-client where clients initiate connections
to central server for file requests and transfers
"""

import socket
import threading

# Host binds to local server IP
host = '127.0.0.1'
port = 3300

# Enter total no. of clients
total_clients = int(input('Enter the number of clients: '))

BUFFER_SIZE = 1024
dashes = '---->'

# Multithreading: handles individual client connections
def client_handling(conn, idx):
    try:
        # Receiving file data, copy to new file
        filename = f'output{idx}.txt'  # idx is client conn no.
        with open(filename, 'w') as fo:
            while True:
                data = conn.recv(BUFFER_SIZE).decode()
                if not data:
                    break
                fo.write(data)

        print(f'Received file successfully! New file name is {filename}')
        # Add file preview (first line if .txt)
        with open(filename, 'r') as fi:
            data = fi.readline()
            print('File preview: ', data)

    except Exception as e:
        print(f'Error handling client {idx}: {e}')
    finally:
        conn.close()  # close connection


# Server Setup
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_tcp:
    server_tcp.bind((host, port))
    server_tcp.listen(total_clients)
    # wait for client connection
    print('[*] Waiting for connection')  # on {host}:{port}

    while True:
        # establish client connections
        connections = []
        print('[*] Initiating clients')
        for i in range(total_clients):
            conn, addr = server_tcp.accept()
            connections.append((conn, i+1))  # store connection, client index
            print('[*] Connected with client', i+1)
            # print(f'[*] Established connection from IP {addr[0]} port: {addr[1]}')

        # Handle each connection in a separate thread for file upload
        threads = []
        for conn, idx in connections:
            thread = threading.Thread(target=client_handling, args=(conn, idx))
            thread.start()
            threads.append(thread)

        # Once all threads finish
        for thread in threads:
            thread.join()

        print('[*] All clients handled successfully')
