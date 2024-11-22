
#connection management for server
import server_functions

import socket

host = '127.0.0.1'
port = 3300
BUFFER_SIZE = 1024
dashes = '----> '

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server_tcp:
    server_tcp.bind((host,port))
    while True:
        server_tcp.listen(6)
        print('[*] Waiting for connection')
        
        connection, addr = server_tcp.accept()
        with connection:
            print(f'[*] Established connection from IP {addr[0]} port: {addr[1]}')
            file = None
            try:
                while True:
                    data = connection.recv(BUFFER_SIZE)
                    if not data:
                        break

                    if file == None:
                        file = open('Files/output.txt', 'wb')
                    else:
                        file = open('Files/output.txt', 'ba')

                    print('Writing')
                    file.write(data)
                    print('Done writing')

                    print('[*] Data received: {}'.format(data.decode('utf-8')))
                    connection.send('file recieved!'.encode('utf-8'))
                    #connection.send(''.encode('utf-8'))
            finally:
                if file != None:
                    file.close()
            