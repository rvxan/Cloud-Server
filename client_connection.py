from client_functions import *

#host = '127.0.0.1'
#port = 3300


# To Do:
# Testing environment on laptop
# Functions to: connect, Authenticate, Upload, Download, Delete, View Dir, Creade/Delete/Secure subfolder
# Hide/prevent access to certain files and directories
# Error handling
# Multithreading

# immediate todo:
# before sending file, send preliminary info to server: what kind of operation to perform, location of file, maybe buffer size

# initial message format:
# signature "ntwrkprj"
# integer representing type of request
# integer representing size of next message
# data to be processed by server


# change this to generally initialize a connection with the ping request
def setup_connection(host, port, username, password):
    # TCP automatically handles resending packets+out of order packets. Robust packet management probs isn't necessary

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_tcp:
        client_tcp.connect((host, port))
        # client_tcp.send(message.encode('utf-8'))

        # with open('TestingTextASCII.txt', 'rb') as file:
        #    send_file(file, client_tcp)

        request = ClientRequest()
        request.ping_request()
        # request.message_request('Testing Message!')
        stream = io.BytesIO(request.to_byte_data())

        if crashServer == True:
            request.type = -1
        print(request.to_byte_data())
        request.send_request(client_tcp)

        type_no, size, buffer_size = header_from_response(client_tcp)
        message = string_from_response(client_tcp)
        print(type_no)
        print(message)

    yield


crashServer = False
