
import socket

host = '34.44.136.98'
#host = '203.0.113.0'
#host = '0.0.0.0'
port = 3300

BUFFER_SIZE = 1024

#To Do:
#Testing environment on laptop
#Functions to: connect, Authenticate, Upload, Download, Delete, View Dir, Creade/Delete/Secure subfolder
#Hide/prevent access to certain files and directories
#Error handling
#Multithreading

def setup_connection():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
        client_tcp.connect((host, port))
        
        client_tcp.send(message.encode('utf-8'))
        data = client_tcp.recv(BUFFER_SIZE)
        yield print(f'The message recieved from the server: {data.decode("utf-8")}')
if __name__ == '__main__':
    while True:
        message = input('enter a message or q for quit: ')
        if message == 'q':
           quit()
        next(setup_connection())