import socket
import struct
import io

BUFFER_SIZE = 1024

RESPONSE_HEADER_SIZE = struct.calcsize('!ill')

#functions on client side get process data and files

# request types 0 = ping, 1 = send message to log, 2 = unused, 3 = upload file, 4 = download file, 5 = delete file/subfolder, 6 = view dir, 7 = change dir, 8 = create subfolder

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

    # intializes a request to upload a file at path 'file' with filename string 'filename' local to the current directory at the server
    def upload_request(self, file, filename):
        self.type = 3
        self.file = file
        self.filename = filename

    # initializes a request to download a file object with filename string 'filepath'
    def download_request(self, filepath):
        self.type = 4
        self.filepath = filepath

    # initializes a delete request to delete a file object with filename string 'filepath'
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

    # the returned data of this function depends on self.type
    # server side will use packed number to determine how to unpack data
    def to_byte_data(self):
        # all requests always start with a signature and request type
        # if signature is invalid, server won't send a return message
        data = struct.pack('!8si', b'ntwrkprj', self.type)
        if self.type == 1:
            encodedMessage = self.message.encode('utf-8')
            data += struct.pack('!i', len(encodedMessage))
            data += encodedMessage

        return data

    def send_request(self, client_tcp):
        send_data(self.to_byte_data(), client_tcp)

# returns (int,long,long) , where the int determines if server responded with a message string 0 or a file 1, and the first long indicates the size of total message, and the last long indicates the buffer size
def header_from_response(client_tcp):
    return struct.unpack('!ill', client_tcp.recv(BUFFER_SIZE, socket.MSG_PEEK)[0:RESPONSE_HEADER_SIZE])


# reads string data from the socket until socket is empty, returns a string
def string_from_response(client_tcp):
    dataHold = b''
    data = client_tcp.recv(BUFFER_SIZE)
    type_no, size, buffer_size = struct.unpack('!ill', data[0:RESPONSE_HEADER_SIZE])
    if type_no != 0:
        raise Exception('this response doesn\'t contain a message')

    dataHold += data[RESPONSE_HEADER_SIZE:]
    size -= BUFFER_SIZE - RESPONSE_HEADER_SIZE
    while size > 0:
        data = client_tcp.recv(buffer_size)
        dataHold += data
        size -= buffer_size
    return dataHold.decode('utf-8')


# reads bytes file data from the socket into the file 'file'
def file_from_response(client_tcp, file):
    pass


# send data to the server using a provided stream and a socket
def send_stream(stream, client_tcp):
    while True:
        data = stream.read(BUFFER_SIZE)
        if data == b'':
            break
        client_tcp.send(data)

    # data = client_tcp.recv(BUFFER_SIZE)
    # print(f'The message recieved from the server: {data.decode("utf-8")}')


# send data to the server using a provided data and a socket
def send_data(data, client_tcp):
    send_stream(io.BytesIO(data), client_tcp)
