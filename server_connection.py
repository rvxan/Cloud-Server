# connection management for server

import struct
import io
import os
import socket
import threading

import time


class RequestHandler:
    pass

print(socket.gethostbyname_ex(socket.gethostname())[2][0])

host = socket.gethostbyname_ex(socket.gethostname())[2][0]
port = 3300
BUFFER_SIZE = 1024

HEADER_SIZE = struct.calcsize('!8si')
STRUCT_INT_SIZE = struct.calcsize('!i')
STRUCT_LONG_SIZE = struct.calcsize('!q')  # q is LONG LONG


# send data to the client using a provided stream and a socket
def send_stream(stream, connection):
    while True:
        data = stream.read(BUFFER_SIZE)
        if data == b'':
            break
        connection.send(data)


# send data to the client using a provided byte array and a socket
def send_data(data, connection):
    send_stream(io.BytesIO(data), connection)


# sends a message 'strMessage' to client through socket 'connection'
def send_string(strMessage, connection):
    messageData = strMessage.encode('utf-8')
    message = struct.pack('!iq', 0, len(messageData)) + messageData
    send_data(message, connection)


# sends a message 'strMessage' to client through socket 'connection', labeled as response type 2: error
def send_error(strMessage, connection):
    messageData = strMessage.encode('utf-8')
    message = struct.pack('!iq', 2, len(messageData)) + messageData
    send_data(message, connection)


def send_file(filepath, connection):
    with open(filepath, 'rb') as file:
        file_size = os.stat(filepath).st_size
        message = struct.pack('!iq', 1, file_size)
        if file_size > BUFFER_SIZE - struct.calcsize('!iq'):
            message += file.read(BUFFER_SIZE - struct.calcsize('!iq'))
            send_data(message, connection)
            send_stream(file, connection)
        else:
            message += file.read(file_size)
            send_data(message, connection)


# reads a string from data and a socket, where data is the first packet containing the string, offset is the non-string info of the packet, and size is the size of the string (including this packet)
def read_string_from_request(connection, data, offset, size):
    dataHold = b''

    dataHold += data[offset:min(len(data), size + offset)]
    # if data already contains entire string, reat that and just adjust offset
    if size + offset < len(data):
        return dataHold.decode('utf-8'), size + offset

    # size is remaining amount to be read
    size -= len(data) - offset

    while size > 0:
        data = connection.recv(BUFFER_SIZE)
        if size > len(data):
            dataHold += data
            size -= len(data)
        else:
            dataHold += data[0:size]
            return dataHold.decode('utf-8'), size

    return dataHold.decode('utf-8'), len(data)


def read_file_from_request(connection, data, offset, size, filepath):
    with open(filepath, 'wb') as file:
        file.write(data[offset:min(len(data), size + offset)])

        # If data already contains entire file, read that and just adjust offset
        if size + offset < len(data):
            return size + offset

        # size is remaining amount to be read
        size -= len(data) - offset

        while size > 0:
            data = connection.recv(BUFFER_SIZE)
            if size > len(data):
                file.write(data)
                size -= len(data)
            else:
                file.write(data[0:size])
                return size

    return len(data)


def handle_connection(connection):
    with connection:
        # print(f'[*] Established connection from IP {addr[0]} port: {addr[1]}')

        main_server_dir = os.getcwd()
        file = None
        try:
            while True:
                # print("con")
                data = connection.recv(BUFFER_SIZE)

                # short circuiting
                if data == None or len(data) < 8:
                    break

                signature, req_type = struct.unpack('!8si', data[0:HEADER_SIZE])
                if signature != b'ntwrkprj':
                    break
                print(req_type)

                # request types 0 = ping, 1 = send message to log, 2 = check if file can be uploaded, 3 = upload file, 4 = download file, 5 = delete file/subfolder, 6 = view dir, 7 = change dir, 8 = create subfolder
                try:
                    # if True:
                    if req_type == 0:  # ping
                        send_string('Ping request from client recieved!', connection)

                    elif req_type == 1:  # print message to console
                        size = struct.unpack('!i', data[HEADER_SIZE:HEADER_SIZE + STRUCT_INT_SIZE])[0]
                        message, offset = read_string_from_request(connection, data, HEADER_SIZE + STRUCT_INT_SIZE,
                                                                   size)

                        print(message)
                        send_string('Message recieved!', connection)

                    elif req_type == 2:  # check if file exists in server
                        size = struct.unpack('!i', data[HEADER_SIZE:HEADER_SIZE + STRUCT_INT_SIZE])[0]
                        path_name, offset = read_string_from_request(connection, data, HEADER_SIZE + STRUCT_INT_SIZE,
                                                                     size)

                        # if file is not in allowed directory
                        if os.path.realpath(path_name).startswith(main_server_dir) == False:
                            raise Exception("Access not authorized in this location")

                        if (os.path.exists(path_name)):
                            send_string('true', connection)
                        else:
                            send_string('false', connection)

                    elif req_type == 3:  # upload file to server
                        offset = HEADER_SIZE
                        path_size = struct.unpack('!i', data[offset:offset + STRUCT_INT_SIZE])[0]
                        offset += STRUCT_INT_SIZE
                        path_name, offset = read_string_from_request(connection, data, offset, path_size)
                        file_size = struct.unpack('!q', data[offset:offset + STRUCT_LONG_SIZE])[0]

                        # if file is not in allowed directory
                        if os.path.realpath(path_name).startswith(main_server_dir) == False:
                            print(os.path.realpath(path_name), main_server_dir)
                            raise Exception("Access not authorized in this location")

                        offset += STRUCT_LONG_SIZE
                        offset = read_file_from_request(connection, data, offset, file_size, path_name)

                        send_string('File recieved!', connection)
                        time.sleep(3)


                    elif req_type == 4:  # download file from server
                        size = struct.unpack('!i', data[HEADER_SIZE:HEADER_SIZE + STRUCT_INT_SIZE])[0]
                        path_name, offset = read_string_from_request(connection, data, HEADER_SIZE + STRUCT_INT_SIZE,
                                                                     size)

                        # if file is not in allowed directory
                        if os.path.realpath(path_name).startswith(main_server_dir) == False:
                            raise Exception("Access not authorized in this location")

                        if os.path.exists(path_name):
                            send_file(path_name, connection)
                        else:
                            send_string("File does not exist", connection)

                    elif req_type == 5:  # delete file from server
                        size = struct.unpack('!i', data[HEADER_SIZE:HEADER_SIZE + STRUCT_INT_SIZE])[0]
                        path_name, offset = read_string_from_request(connection, data, HEADER_SIZE + STRUCT_INT_SIZE,
                                                                     size)

                        # if file is not in allowed directory
                        if os.path.realpath(path_name).startswith(main_server_dir) == False:
                            raise Exception("Access not authorized in this location")

                        os.remove(path_name)
                        send_string('File deleted!', connection)

                    elif req_type == 6:  # view dir
                        # Combined string of current directory contents
                        dirInfo = f"Current Directory: {os.getcwd()}\nContents:\n" + "\n".join(os.listdir())
                        send_string(dirInfo, connection)

                    elif req_type == 7:  # change dir
                        size = struct.unpack('!i', data[HEADER_SIZE:HEADER_SIZE + STRUCT_INT_SIZE])[0]
                        path_name, offset = read_string_from_request(connection, data, HEADER_SIZE + STRUCT_INT_SIZE,
                                                                     size)

                        # if file is not in allowed directory
                        if os.path.realpath(path_name).startswith(main_server_dir) == False:
                            raise Exception("Access not authorized in this location")

                        if os.path.exists(path_name):
                            current_dir = os.chdir(path_name)
                            send_string('Changed Dir!', connection)
                        else:
                            send_string('Directory does not exist', connection)

                    elif req_type == 8:  # create subfolder
                        size = struct.unpack('!i', data[HEADER_SIZE:HEADER_SIZE + STRUCT_INT_SIZE])[0]
                        path_name, offset = read_string_from_request(connection, data, HEADER_SIZE + STRUCT_INT_SIZE,
                                                                     size)

                        # if file is not in allowed directory
                        if os.path.realpath(path_name).startswith(main_server_dir) == False:
                            raise Exception("Access not authorized in this location")

                        if not os.path.exists(path_name):
                            os.mkdir(path_name)
                            send_string('Subfolder created', connection)
                        else:
                            send_string('Subfolder already exists', connection)

                    elif req_type == 9:  # delete subfolder
                        size = struct.unpack('!i', data[HEADER_SIZE:HEADER_SIZE + STRUCT_INT_SIZE])[0]
                        path_name, offset = read_string_from_request(connection, data, HEADER_SIZE + STRUCT_INT_SIZE,
                                                                     size)

                        # if file is not in allowed directory
                        if os.path.realpath(path_name).startswith(main_server_dir) == False:
                            raise Exception("Access not authorized in this location")

                        if os.path.exists(path_name):
                            os.rmdir(path_name)
                            send_string('Subfolder deleted', connection)
                        else:
                            send_string('Subfolder does not exist', connection)

                    elif req_type == -1:
                        send_string('SERVER CRASHED', connection)
                        print('manually crashed from client')
                        raise SystemExit()
                        return
                    else:
                        raise Exception('invalid request type: ' + str(req_type))
                except Exception as e:  # handle errors occuring during response
                    # if client was not currently reading a packet, then server won't crash
                    send_string(str(e), connection)

        finally:
            if file != None:
                file.close()


if __name__ == '__main__':
    # may throw an error if an invalid or corrupted packet is sent to the server
    if not os.path.exists("Files"):
        os.mkdir("Files")
    os.chdir('Files')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_tcp:
        server_tcp.bind((host, port))
        while True:
            server_tcp.listen(6)
            print('[*] Waiting for connection')

            connection, addr = server_tcp.accept()
            threading.Thread(target=handle_connection, args=(connection,)).start()
