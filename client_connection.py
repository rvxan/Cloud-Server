import socket
import struct
import io
import os

host = '34.55.36.129'
port = 3300

BUFFER_SIZE = 1024

RESPONSE_HEADER_SIZE = struct.calcsize('!iq')

# request types 0 = ping, 1 = send message to log, 2 = request upload, 3 = upload file, 4 = download file, 5 = delete file, 6 = view dir, 7 = change dir, 8 = create subfolder, 9 = delete subfolder

# class to setup and organize data to be sent to the server in a single pass
class ClientRequest:
    def __init__(self):
        self.ping_request()

    # initializes a ping for this request
    def ping_request(self):
        self.type = 0

    # intializes a message request for a string 'message'
    def message_request(self, message):
        self.type = 1
        self.message = message

    # initializes a request to check if a filename exists on the server
    def upload_test_request(self, filename):
        self.type = 2
        self.filename = filename

    # intializes a request to upload a local file at 'filepath' to the current directory at the server
    def upload_request(self, filepath, filename):
        self.type = 3
        self.filepath = filepath
        self.filename = filename

    # initializes a request to download a file object with at 'filepath'
    def download_request(self, filepath):
        self.type = 4
        self.filepath = filepath

    # initializes a delete request to delete a file object at 'filepath'
    def delete_request(self, filepath):
        self.type = 5
        self.filepath = filepath

    # initalizes a dir request to obtain a string representation of the current directory at the server
    def viewdir_request(self):
        self.type = 6

    # initializes a change directory request on the server using a string 'dirname'
    def changedir_request(self, dirname):
        self.type = 7
        self.dirname = dirname

    # initializes a create subfolder request on the server using a string 'dirname'
    def createdir_request(self, dirname):
        self.type = 8
        self.dirname = dirname

    # initializes a delete subfolder request on the server using a string 'dirname'
    def deletedir_request(self, dirname):
        self.type = 9
        self.dirname = dirname

    # the returned data of this function depends on self.type
    # server side will use packed number to determine how to unpack data
    def send_request(self, client_tcp):
        # all requests always start with a signature and request type
        # if signature is invalid, server won't send a return message

        socket_send = SocketSend(client_tcp)

        socket_send.send_bytes(struct.pack('!8si', b'ntwrkprj', self.type))
        if self.type == 0:
            pass
        elif self.type == 1:
            socket_send.send_string(self.message)
        elif self.type == 2:
            socket_send.send_string(self.filename)
        elif self.type == 3:
            socket_send.send_string(self.filename)
            socket_send.send_file(self.filepath)
        elif self.type == 4:
            socket_send.send_string(self.filepath)
        elif self.type == 5:
            socket_send.send_string(self.filepath)
        elif self.type == 6:
            pass
        elif self.type == 7:
            socket_send.send_string(self.dirname)
        elif self.type == 8:
            socket_send.send_string(self.dirname)
        elif self.type == 9:
            socket_send.send_string(self.dirname)
        socket_send.flush()


# class to queue data sending
class SocketSend:
    def __init__(self, socket):
        self.socket = socket
        self.data_size = 0
        self.data = b''

    def send_string(self, message):
        encodedMessage = message.encode('utf-8')
        self.send_bytes(struct.pack('!i', len(encodedMessage)))
        self.send_bytes(encodedMessage)

    def send_file(self, filepath):
        self.send_bytes(struct.pack('!q', os.stat(filepath).st_size))
        with open(filepath, 'rb') as file:
            while True:
                file_data = file.read(BUFFER_SIZE)
                if file_data == b'':
                    break
                self.send_bytes(file_data)

    def send_bytes(self, new_data):
        max_write_size = BUFFER_SIZE - self.data_size
        if (len(new_data) > max_write_size):
            self.data += new_data[0:max_write_size]
            self.socket.send(self.data)
            # reset data
            self.data = new_data[max_write_size:len(new_data)]
            self.data_size = len(new_data) - max_write_size
        else:
            self.data += new_data[0:max_write_size]
            self.data_size += len(new_data)

    def flush(self):
        self.socket.send(self.data)


# returns (int,long) , where the int determines if server responded with a message string 0 or 2, or a file 1, and the first long indicates the size of total message
def header_from_response(client_tcp):
    return struct.unpack('!iq', client_tcp.recv(BUFFER_SIZE, socket.MSG_PEEK)[0:RESPONSE_HEADER_SIZE])


# reads string data from the socket until socket is empty, returns a string
def string_from_response(client_tcp):
    dataHold = b''
    data = client_tcp.recv(BUFFER_SIZE)
    type_no, size = struct.unpack('!iq', data[0:RESPONSE_HEADER_SIZE])
    if type_no != 0 and type_no != 2:
        raise Exception('this response doesn\'t contain a message')

    dataHold += data[RESPONSE_HEADER_SIZE:]
    size -= len(data) - RESPONSE_HEADER_SIZE
    while size > 0:
        data = client_tcp.recv(BUFFER_SIZE)
        dataHold += data
        size -= len(data)
    return dataHold.decode('utf-8')


# reads bytes file data from the socket into the file path string 'filepath'
def file_from_response(client_tcp, filepath):
    with open(filepath, 'wb') as file:
        data = client_tcp.recv(BUFFER_SIZE)
        type_no, size = struct.unpack('!iq', data[0:RESPONSE_HEADER_SIZE])

        if type_no != 1:
            raise Exception('this response doesn\'t contain a file')

        file.write(data[RESPONSE_HEADER_SIZE:])
        size -= len(data) - RESPONSE_HEADER_SIZE
        while size > 0:
            data = client_tcp.recv(BUFFER_SIZE)
            file.write(data)
            size -= len(data)


# send data to the server using a provided stream and a socket
def send_stream(stream, client_tcp):
    while True:
        data = stream.read(BUFFER_SIZE)
        if data == b'':
            break
        client_tcp.send(data)


def write_file_to_data(data, filepath):
    with open(filepath, 'rb') as file:
        while True:
            file_data = file.read(BUFFER_SIZE)
            print(data)
            if file_data == b'':
                break
            data += file_data
    return data


# send data to the server using a provided data and a socket
def send_data(data, client_tcp):
    send_stream(io.BytesIO(data), client_tcp)
