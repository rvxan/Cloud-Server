from client_connection import *
import ipaddress

# Breaks input into requested number of values
def parse_message(message, splits):
    # Split the input string into parts by spaces
    parts = message.strip().split(" ")

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

isConnected = 0

while not isConnected:
    message = input('Enter connect followed by an IP, port, username, and password to connect to a server, h for help, or q for quit: ')
    command, host, port, username, password = parse_message(message, 5)
    print(command, host, port, username, password)
    if command.lower() == 'connect':
        if is_valid_ip(host) and port.isdigit() and 1 <= int(port) <= 65535:
            isConnected = 1
            #setup_connection(host, port, username, password)
        else:
            print("Host or port is invalid.")
    elif command == 'test':
        isConnected = 1
    elif command == 'h':
        print("connect [\033[3mServer IP\033[0m] [\033[3mPort\033[0m] - Connect to server at specified IP and port")
    elif command == 'q':
        quit()
    else:
        print("Command not recognized.")

while isConnected:
    request = ClientRequest()
    message = input('Enter a command, h for help, or q to disconnect: ')
    command, att1, att2 = parse_message(message, 3)
    print(command, att1, att2)
    if command.lower() == 'h':
        print("upload [\033[3mfilepath\033[0m] [\033[3mfilename\033[0m] - Upload file located at \033[3mfilepath\033[0m to current server directory under the name \033[3mfilename\033[0m"
              "\n                                   If a file name is not given, the file's existing name will be used."
              "\ndownload [\033[3mfilepath\033[0m] - Download file located at \033[3mfilepath\033[0m from server"
              "\ndelete [\033[3mfilepath\033[0m] - Delete file located at \033[3mfilepath\033[0m from server"
              "\ndir - View files and subdirectories"
              "\ncd [\033[3mdirectory\033[0m] - Change directory to [\033[3mdirectory\033[0m] in server")
        continue
    elif command.lower() == 'q':
        print("isConnected = 0")
        isConnected = 0
        continue
    elif command.lower() == 'upload':
        if att1 == "":
            print("When using the upload command, please specify a file to upload")
            continue
        print("request.upload_request(att1, att2)")
        #request.upload_request(att1, att2)
    elif command.lower() == 'download':
        if att1 == "":
            print("When using the download command, please specify a file to download")
            continue
        print("request.download_request(att1)")
        #request.download_request(att1)
    elif command.lower() == 'delete':
        if att1 == "":
            print("When using the delete command, please specify a file to delete")
            continue
        print("request.delete_request(att1)")
        #request.delete_request(att1)
    elif command.lower() == 'dir':
        print("request.viewdir_request()")
        #request.viewdir_request()
    elif command.lower() == 'cd':
        if att1 == "":
            print("When using the change directory command, please specify a target directory")
            continue
        print("request.changedir_request(att1)")
        #request.changedir_request(att1)
    else:
        print("Command not recognized.")
        continue
    print("Exit test")