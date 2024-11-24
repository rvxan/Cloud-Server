from client_connection import *


def parse_input(input, splits):
    # Split the input string into parts by spaces
    parts = input.strip().split(" ")

    # Pad the list with empty strings if fewer parts than num_parts
    parts += [""] * (splits - len(parts))

    return tuple(parts[:splits])

while True:
    message = input('Enter connect followed by an IP, port, username, and password to connect to a server, h for help, or q for quit: ')
    request, host, port, username, password = parse_input(message, 5)
    print(request, host, port, username, password)
    if message == 'connect':
        setup_connection(host, port, username, password)
    elif message == 'h':
        print("connect [\033[3mServer IP\033[0m] [\033[3mPort\033[0m] - Connect to server at specified IP and port")
    elif message == 'q':
        quit()
    else:
        print("Command not recognized. For help, )
