
#connection management for server
import server_functions
import struct
import io
import os

import socket

class RequestHandler:
    pass

host = '127.0.0.1'
port = 3300
BUFFER_SIZE = 1024

HEADER_SIZE = struct.calcsize('!8si')
STRUCT_INT_SIZE = struct.calcsize('!i')
STRUCT_LONG_SIZE = struct.calcsize('!l')


#send data to the client using a provided stream and a socket
def send_stream(stream, connection):
    while True:
        data = stream.read(BUFFER_SIZE)
        if data == b'':
            break
        connection.send(data)
#send data to the client using a provided byte array and a socket
def send_data(data, connection):
    send_stream(io.BytesIO(data),connection)

#sends a message 'strMessage' to client through socket 'connection'
def send_string(strMessage, connection):
    messageData = strMessage.encode('utf-8')
    message = struct.pack('!il', 0, len(messageData)) + messageData
    send_data(message, connection)

def send_file(filepath, connection):
    with open(filepath, 'rb') as file:
        file_size = os.stat(filepath).st_size
        message = struct.pack('!il', 1, file_size)
        if file_size > BUFFER_SIZE - struct.calcsize('!il'):
            message += file.read(BUFFER_SIZE - struct.calcsize('!il'))
            send_data(message, connection)
            send_stream(file, connection)
        else:
            message ++ file.read(file_size)
            send_data(message, connection)

#reads a string from data and a socket, where data is the first packet containing the string, offset is the non-string info of the packet, and size is the size of the string (including this packet)
def read_string_from_request(connection, data, offset, size):
    dataHold = b''

    dataHold += data[offset:min(BUFFER_SIZE,size+offset)]
    if size+offset < BUFFER_SIZE:
        return dataHold.decode('utf-8'), size+offset
    
    size -= BUFFER_SIZE-offset
    while size > BUFFER_SIZE:
        data = connection.recv(BUFFER_SIZE)
        dataHold += data
        size -= BUFFER_SIZE
    if size > 0:
        data = connection.recv(BUFFER_SIZE, socket.MSG_PEEK)
        dataHold += data[0:size]
    else:
        size = 0
    return dataHold.decode('utf-8'), size

def read_file_from_request(connection, data, offset, size, filepath):
    
    with open(filepath, 'wb') as file:
        file.write(data[offset:min(BUFFER_SIZE,size+offset)])
        if size+offset < BUFFER_SIZE:
            return size+offset

        size -= BUFFER_SIZE-offset

        while size > BUFFER_SIZE:
            file.write(connection.recv(BUFFER_SIZE))
            size -= BUFFER_SIZE
        if size > 0:
            data = connection.recv(BUFFER_SIZE, socket.MSG_PEEK)
            file.write(data[0:size])
        else:
            size = 0

    return size

def handle_connection(connection):
    with connection:
        print(f'[*] Established connection from IP {addr[0]} port: {addr[1]}')

        file = None
        try:
            while True:
                data = connection.recv(BUFFER_SIZE)

                #short circuiting
                if data == None or len(data) < 8:
                    break

                signature, req_type = struct.unpack('!8si',data[0:HEADER_SIZE])
                if signature != b'ntwrkprj':
                    break
                print(req_type)

                #request types 0 = ping, 1 = send message to log, 2 = unused, 3 = upload file, 4 = download file, 5 = delete file/subfolder, 6 = view dir, 7 = change dir, 8 = create subfolder 
                if req_type == 0: #ping
                    send_string('Ping request from client recieved!', connection)
                    break
                elif req_type == 1: #print message to console
                    size = struct.unpack('!i', data[HEADER_SIZE:HEADER_SIZE+STRUCT_INT_SIZE])[0]
                    message, offset = read_string_from_request(connection, data, HEADER_SIZE+STRUCT_INT_SIZE,size)
                    print(message)
                    send_string('Message recieved!', connection)
                    break
                elif req_type == 3: #upload file to server
                    offset = HEADER_SIZE
                    path_size = struct.unpack('!i', data[offset:offset+STRUCT_INT_SIZE])[0]
                    offset += STRUCT_INT_SIZE
                    path_name, offset = read_string_from_request(connection, data, offset, path_size)
                    #offset += path_size
                    print(data[offset:offset+STRUCT_INT_SIZE])
                    file_size = struct.unpack('!l', data[offset:offset+STRUCT_LONG_SIZE])[0]
                    print(file_size)
                    offset += STRUCT_LONG_SIZE
                    offset = read_file_from_request(connection, data, offset, file_size, path_name)
                    send_string('File recieved!', connection)
                elif req_type == 4: #download file from server
                    size = struct.unpack('!i', data[HEADER_SIZE:HEADER_SIZE+STRUCT_INT_SIZE])[0]
                    filename, offset = read_string_from_request(connection, data, HEADER_SIZE+STRUCT_INT_SIZE,size)
                    send_file(filename, connection)
                else:
                    raise Exception('invalid request type: ' + str(req_type))

                #if file == None:
                #    file = open('Files/output.txt', 'wb')
                #else:
                #    file = open('Files/output.txt', 'ba')

                #print('Writing')
                #file.write(data)
                #print('Done writing')

                #print('[*] Data received: {}'.format(data.decode('utf-8')))


                #connection.send('file recieved!'.encode('utf-8'))
                #connection.send(''.encode('utf-8'))
        finally:
            if file != None:
                file.close()


if __name__ == '__main__':

    #may throw an error if an invalid or corrupted packet is sent to the server
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server_tcp:
        server_tcp.bind((host,port))
        while True:
            server_tcp.listen(6)
            print('[*] Waiting for connection')

            #whenever the client want's to make a new request, a new connection must be opened
            #prevents problems if a user opens a connection, then forgets that it was open
            connection, addr = server_tcp.accept()
            handle_connection(connection)
