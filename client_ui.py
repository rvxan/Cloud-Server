
from client_connection import *
import ipaddress
import shlex
import time

from network_analysis import *

client_tcp = None

# Attempts to setup the connection to the server using the specified host and port
def setup_connection(host, port):

    global client_tcp
    client_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_tcp.connect((host, port))
    except socket.error as e:
        client_tcp = None
        print(f"Error connecting to {host}:{port} - {e}")
        return


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

# Display user inputs
while True:
    # If not connected, display connection input
    while not client_tcp:
        # Get user input and split into separate parts
        message = input('Enter connect followed by an IP, port, username, and password to connect to a server, h for help, or q for quit: ')
        command, host, port = parse_message(message, 3)

        # If connect is followed by a valid host and port, attempt connection
        if command.lower() == 'connect':
            if port.isdigit():
                port = int(port)
                if is_valid_ip(host) and 1 <= port <= 65535:
                    setup_connection(host, port)
                else:
                    print("Host or port is invalid.")
            else:
                print("Port should be an integer")

        # Displays syntax for connect command
        elif command == 'h':
            print("connect [\033[3mServer IP\033[0m] [\033[3mPort\033[0m] - Connect to server at specified IP and port")

        # Closes client_ui.py
        elif command == 'q':
            quit()

        # If command is not recognized, inform user
        else:
            print("Command not recognized.")

    # If connected, display command input
    while client_tcp:
        # Variable to prevent attempting to send uninitialized requests
        shouldSend = 1
        request = ClientRequest()
        # Get user input and split into separate parts
        message = input('Enter a command, h for help, or q to disconnect: ')
        command, att1, att2 = parse_message(message, 3)

        # Displays syntax for all commands
        if command.lower() == 'h':
            print("upload [filepath] - Upload file located at [filepath] to current server directory"
                  "\ndownload [filepath] - Download file located at [filepath] from server"
                  "\ndelete [filepath] - Delete file located at filepath from server"
                  "\ndir - View files and subdirectories"
                  "\ncd [directory] - Change directory to [directory] in server, use '..' to ascend a directory"
                  "\nsubfolder [create/delete] [directory] - Create/delete a subfolder named [directory]"
                  "\nping - Ping the server and print the response time")
            continue

        # Disconnect from server
        elif command.lower() == 'q':
            client_tcp.close()
            client_tcp = None
            continue

        # Upload file to server
        elif command.lower() == 'upload':

            # If file path is not valid, don't attempt to upload
            if not os.path.isfile(att1):
                print("File is invalid")
                continue

            # If file path is valid, check with server if name is free to use
            request.upload_test_request(os.path.basename(att1))
            request.send_request(client_tcp)

            # If the name is in use, ask the client if they would like to replace the file
            if header_from_response(client_tcp)[0] == 0:
                if string_from_response(client_tcp) == "true":
                    while True:
                        message = input('A file of that name already exists in the current server directory'
                                        '\nWould you like to overwrite this file <Y/N>: ')
                        # If the client wants to replace the file, initialize upload request
                        if message.upper() == "Y":
                            request.upload_request(os.open(att1, os.O_RDONLY), os.path.basename(att1))
                            break
                        # If the client does not want to replace the file, do not send a request this loop
                        elif message.upper() == "N":
                            shouldSend = 0
                            break
                        # If input is invalid, inform user
                        else:
                            print("Please enter Y or N")
                # If the name is not in use, initialize upload request
                else:
                    request.upload_request(os.open(att1, os.O_RDONLY), os.path.basename(att1))
            # If the server replies with an error, do not send a request this loop
            elif header_from_response(client_tcp)[0] == 2:
                shouldSend = 0

        # Download a file from the server
        elif command.lower() == 'download':
            # If the file path is blank, remind user to specify file path
            if att1 == "":
                print("When using the download command, please specify a file to download")
                continue
            # If the file path is not blank, initialize download request
            request.download_request(att1)

        # Delete a file from the server
        elif command.lower() == 'delete':
            # If the file path is blank, remind user to specify file path
            if att1 == "":
                print("When using the delete command, please specify a file to delete")
                continue
            # If the file path is not blank, initialize delete request
            request.delete_request(att1)
        # View directory contents
        elif command.lower() == 'dir':
            # Initialize directory view request
            request.viewdir_request()
        # Change directory
        elif command.lower() == 'cd':
            # If the directory name is blank, remind user to specify directory name
            if att1 == "":
                print("When using the change directory command, please specify a target directory")
                continue
            # If the directory name is not blank, initialize a directory change request
            request.changedir_request(att1)

        # Subfolder commands
        elif command.lower() == 'subfolder':
            # If the directory name is blank, remind user to specify directory name
            if att2 == "":
                print("When using the subfolder command, please specify a subfolder name to modify")
                break
            # If the user requests to create a directory, initialize a create directory request
            if att1.lower() == 'create':
                request.createdir_request(att2)
            # If the user requests to delete a directory, initialize a delete directory request
            elif att1.lower() == 'delete':
                request.deletedir_request(att2)
            # If the argument is not recognized, inform user
            else:
                print("When using the subfolder command, specify if you would like to create or delete a subfolder")
                break

        # Ping the server and print the response time
        elif command.lower() == 'ping':
            request.ping_request()
            startTime = time.time()
            request.send_request(client_tcp)
            string_from_response(client_tcp)
            endTime = time.time()
            calculate_latency(startTime, endTime)
            continue

        # Does nothing ;3c
        elif command.lower() == 'p':
            request.ping_request()
            request.type = -1
        # If command is not recognized, inform user
        else:
            print("Command not recognized.")
            continue

        # If a request should not be sent, skip the code below
        if not shouldSend:
            continue

        # Send the request initialized above to the server and await a response
        request.send_request(client_tcp)
        responseType = header_from_response(client_tcp)[0]

        # If the response is a string, print it
        if responseType == 0 or responseType == 2:
            print(string_from_response(client_tcp))

        # If the response is a file, save it in the downloads directory under the name used in the download command
        elif responseType == 1:
            # Create downloads directory if it does not exist
            if not os.path.exists("downloads"):
                os.mkdir("downloads")
            file_from_response(client_tcp, os.getcwd() + "\\downloads\\" + os.path.basename(att1))
        # Response from server is of unknown type, inform user
        else:
            print("Response is not a string, error, or file")
            continue
