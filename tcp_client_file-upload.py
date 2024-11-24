# tcp_client.py
# Cloud-Server Project for Computer Networks

"""
Server-Client Architecture: Implement server-client where clients initiate connections
to central server for file requests and transfers.
"""

import socket
import os

# client and server should match port
host = '127.0.0.1'
port = 3300

BUFFER_SIZE = 1024


# Client function check file type and size before sending to server
def check_file(filename):
    try:
        filesize = os.path.getsize(filename)  # gets filesize in bytes

        # Check file type using the file extension and compare filesize to specified min
        if filename.endswith('.txt'):  # checks text file
            if filesize >= 25 * 1024 * 1024:  # 25MB in bytes
                print(f'[*] Text file {filename} sent to server')
                return 'text'
            else:
                print(f'Error: {filename} must be at least 25MB')
                return None
        elif filename.endswith('.mp3') or filename.endswith('.wav'):  # checks audio file
            if filesize >= 0.5 * 1024 * 1024 * 1024:  # 0.5GB in bytes
                print(f'[*] Audio file {filename} sent to server')
                return 'binary'
            else:
                print(f'Error: {filename} must be at least 0.5GB')
                return None
        elif filename.endswith('.mp4') or filename.endswith('.avi') or filename.endswith('.mov'):  # checks video file
            if filesize >= 2 * 1024 * 1024 * 1024:  # 2GB in bytes
                print(f'[*] Video file {filename} sent to server')
                return 'binary'
            else:
                print(f'Error: {filename} must be at least 2GB')
                return None
        else:
            print(f'File type {filename} not supported.')
            return None
    except FileNotFoundError:
        print(f'Error: File {filename} not found.')
        return None


# Client function sends file to server
def file_send(client_tcp, filename, filetype):
    try:
        if filetype == 'text':
            with open(filename, 'r', encoding='utf-8') as fi:  # open in binary for non-text files
                data = fi.read()
                while data:
                    client_tcp.send(data.encode())
                    data = fi.read()

        if filetype == 'binary':
            with open(filename, 'rb') as fi:  # open in binary for non-text files
                data = fi.read()
                while data:
                    client_tcp.send(data)
                    data = fi.read()

        print(f'[*] File {filename} was sent successfully')
    except IOError:
        print('Error: File not found. Please provide valid filename.')


# Client Setup
if __name__ == '__main__':
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
        try:
            client_tcp.connect((host, port))
            print('[*] Connected to server')  # at {host}:{port}

            while True:
                filename = input('Input filename you want to send (or "q" to quit): ')

                if filename.lower() == 'q':
                    break

                filetype = check_file(filename)
                if filetype:  # If the file is valid, send it
                    file_send(client_tcp, filename, filetype)

        except ConnectionError:
            print(f'Error: Unable to connect to server at {host}:{port}.')
