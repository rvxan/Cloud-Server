import os

from client_connection import *
import ipaddress
import shlex

client_tcp = None

# change this to generally initialize a connection with the ping request
def setup_connection(host, port, username, password):
    # TCP automatically handles resending packets+out of order packets. Robust packet management probs isn't necessary
    global client_tcp
    client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_tcp.connect((host, port))



# Breaks input into requested number of values
def parse_message(message, splits):
    # Use shlex.split to split the input while preserving quoted substrings
    parts = shlex.split(message.strip())

    # Pad the list with empty strings if fewer parts than num_parts
    parts += [""] * (splits - len(parts))

    # Return only the requested number of parts
    return tuple(parts[:splits])

# Check if IP is valid
def is_valid_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

while True:
    while not client_tcp or client_tcp.fileno() == -1:
        message = input('Enter connect followed by an IP, port, username, and password to connect to a server, h for help, or q for quit: ')
        command, host, port, username, password = parse_message(message, 5)
        if command.lower() == 'connect':
            if port.isdigit():
                port = int(port)
                if is_valid_ip(host) and 1 <= port <= 65535:
                    setup_connection(host, port, username, password)
                else:
                    print("Host or port is invalid.")
            else:
                print("Port should be an integer")
        elif command == 'localhost':
            setup_connection('127.0.0.1', 3300, username, password)
        elif command == 'test':
            isConnected = 1
        elif command == 'h':
            print("connect [\033[3mServer IP\033[0m] [\033[3mPort\033[0m] - Connect to server at specified IP and port")
        elif command == 'q':
            quit()
        else:
            print("Command not recognized.")

    while client_tcp.fileno() != -1:
        shouldSend = 1
        request = ClientRequest()
        message = input('Enter a command, h for help, or q to disconnect: ')
        command, att1, att2 = parse_message(message, 3)

        if command.lower() == 'h':
            print("upload [\033[3mfilepath\033[0m] - Upload file located at \033[3mfilepath\033[0m to current server directory"
                  "\ndownload [\033[3mfilepath\033[0m] - Download file located at \033[3mfilepath\033[0m from server"
                  "\ndelete [\033[3mfilepath\033[0m] - Delete file located at \033[3mfilepath\033[0m from server"
                  "\ndir - View files and subdirectories"
                  "\ncd [\033[3mdirectory\033[0m] - Change directory to [\033[3mdirectory\033[0m] in server")
            continue

        elif command.lower() == 'q':
            client_tcp.close()
            continue

        elif command.lower() == 'upload':

            if not os.path.isfile(att1):
                print("File is invalid")
                continue

            request.upload_test_request(os.path.basename(att1))
            request.send_request(client_tcp)

            if header_from_response(client_tcp)[0] == 0:
                if string_from_response(client_tcp) == "true":
                    while True:
                        message = input('A file of that name already exists in the current server directory'
                                        '\nWould you like to overwrite this file <Y/N>: ')
                        if message.upper() == "Y":
                            request.upload_request(os.open(att1, os.O_RDONLY), os.path.basename(att1))
                            break
                        elif message.upper() == "N":
                            shouldSend = 0
                            break
                        else:
                            print("Please enter Y or N")
                else:
                    request.upload_request(os.open(att1, os.O_RDONLY), os.path.basename(att1))
            elif header_from_response(client_tcp)[0] == 2:
                shouldSend = 0
        elif command.lower() == 'download':
            if att1 == "":
                print("When using the download command, please specify a file to download")
                continue
            request.download_request(att1)
        elif command.lower() == 'delete':
            if att1 == "":
                print("When using the delete command, please specify a file to delete")
                continue
            request.delete_request(att1)
        elif command.lower() == 'dir':
            request.viewdir_request()
        elif command.lower() == 'cd':
            if att1 == "":
                print("When using the change directory command, please specify a target directory")
                continue
            request.changedir_request(att1)

        elif command.lower() == 'subfolder':
            if att2 == "":
                print("When using the subfolder command, please specify a subfolder name to modify")
                break
            if att1.lower() == 'create':
                request.createdir_request(att2)
            elif att1.lower() == 'delete':
                request.deletedir_request(att2)
            else:
                print("When using the subfolder command, specify if you would like to create or delete a subfolder")
                break
        elif command.lower() == 'p':
            request.ping_request()
            request.type = -1
        else:
            print("Command not recognized.")
            continue

        if not shouldSend:
            continue

        request.send_request(client_tcp)
        responseType = header_from_response(client_tcp)[0]

        if responseType == 0 or responseType == 2:
            print(string_from_response(client_tcp))
        elif responseType == 1:
            # Receiving file, store in current directory as downloaded file name
            if not os.path.exists("downloads"):
                os.mkdir("downloads")
            file_from_response(client_tcp, os.getcwd() + "\\downloads\\" + os.path.basename(att1))
        else:
            errorStr = string_from_response(client_tcp)
