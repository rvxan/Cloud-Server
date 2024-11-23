
import socket
import struct
import io

import client_functions

host = '127.0.0.1'
port = 3300

BUFFER_SIZE = 1024

#To Do:
#Testing environment on laptop
#Functions to: connect, Authenticate, Upload, Download, Delete, View Dir, Creade/Delete/Secure subfolder
#Hide/prevent access to certain files and directories
#Error handling
#Multithreading

#immediate todo:
#before sending file, send preliminary info to server: what kind of operation to perform, location of file, maybe buffer size

#initial message format:
#signature "ntwrkprj"
#integer representing type of request
#integer representing size of next message
#data to be processed by server

#request types 0 = ping, 1 = send message to log, 2 = unused, 3 = upload file, 4 = download file, 5 = delete file/subfolder, 6 = view dir, 7 = change dir, 8 = create subfolder 

#class to setup and organize data to be sent to the server in a single pass
class ClientRequest:
    def __init__(self):
        self.ping_request()
    #initializes a ping for this request
    def ping_request(self):
        self.type = 0
    
    #intializes a message request for a string 'message'
    def message_request(self, message):
        self.type = 0

    #intializes a request to upload a file object 'file' with filename string 'filepath' local to the current directory at the server
    def upload_request(self, file, filepath):
        self.type = 0

    #initializes a request to download a file object with filename string 'filepath'
    def download_request(self, filepath):
        self.type = 0

    #initializes a delete request to delete a file object with filename string 'filepath'
    def delete_request(self, filepath):
        self.type = 0

    #initalizes a dir request to obtain a string representation of the current directory at the server
    def viewdir_request(self):
        self.type = 0

    #initializes a change directory request on the server using a string 'filepath'
    def changedir_request(self):
        self.type = 0

    #initializes a create subfolder request on the server using a string 'filepath'
    def createdir_request(self):
        self.type = 0

    #the returned data of this function depends on self.type
    #server side will use packed number to determine how to unpack data
    def to_byte_data(self):
        #all requests always start with a signature and request type
        #if signature is invalid, server won't send a return message
        data = struct.pack('8sH', 'ntwrkprj', 0)
        return data

    #see to_byte_data. This is just a wrapper to create a iostream out of the BytesObject returned by that function
    def to_stream_data(self):
        stream = io.BytesIO(self.to_byte_data())
        return stream

#returns int, where int determines if server responded with a message string or a file
def header_from_response(client_tcp):
    pass
#reads string data from the socket, must be called until an empty string is returned
def string_from_response(client_tcp):
    pass
#reads binary file data from the socket, must be called until return value has type None
def file_from_response(client_tcp):
    pass

#send data to the server using a provided stream and a socket
def send_stream(stream, client_tcp):
    while True:
        data = stream.read(BUFFER_SIZE)
        if data == b'':
            break
        client_tcp.send(data)
        print('Sent file')

       #data = client_tcp.recv(BUFFER_SIZE)
       #print(f'The message recieved from the server: {data.decode("utf-8")}')

#change this to generally initialize a connection with the ping request
def setup_connection():
    #TCP automatically handles resending packets+out of order packets. Robust packet management probs isn't necessary
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
        client_tcp.connect((host, port))
        #client_tcp.send(message.encode('utf-8'))
        
        #with open('TestingTextASCII.txt', 'rb') as file:
        #    send_file(file, client_tcp)

        request = ClientRequest()
        request.ping_request()
        stream = io.BytesIO(request.to_byte_data)
        print(request.to_byte_data)
    

    yield


if __name__ == '__main__':
    while True:
        message = input('enter a message or q for quit: ')
        if message == 'q':
           quit()
        next(setup_connection())