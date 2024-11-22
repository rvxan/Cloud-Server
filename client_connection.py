
import socket
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


def setup_connection():
    #Will a Socket Stream implement a "sliding window" of packets, or does it have to be a datagram with explicit management on server side python
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
        client_tcp.connect((host, port))
        
        #client_tcp.send(message.encode('utf-8'))
        with open('TestingTextBig.txt', 'rb') as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if data == b'':
                    break
                client_tcp.send(data)
                print("Sent file")

                data = client_tcp.recv(BUFFER_SIZE)
                print(f'The message recieved from the server: {data.decode("utf-8")}')
        yield print(f'The message recieved from the server: {data.decode("utf-8")}')


if __name__ == '__main__':
    while True:
        message = input('enter a message or q for quit: ')
        if message == 'q':
           quit()
        next(setup_connection())