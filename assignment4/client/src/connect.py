import socket

# GLOBAL VARIABLES
HOST = 'localhost'     
PORT = 65432           
CLIENT_SOCKET = None   
USER_ID = None

def connect_server(user_id):
    # Configure the global variables
    global CLIENT_SOCKET, USER_ID
    USER_ID = user_id
    
    while True:
        HOST = input("Enter the server IP: ")

        try:
            CLIENT_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            CLIENT_SOCKET.connect((HOST, PORT))

            # Send user ID to the server for identification
            CLIENT_SOCKET.sendall(USER_ID.encode())

            print("\nConnection established")
            return 0
        except socket.error as e:
            print("\nError: Could not connect to server")
            print(e)

def get_client():
    global CLIENT_SOCKET
    if CLIENT_SOCKET is not None:
        return CLIENT_SOCKET
    else:
        print("\nNo connection to server. Please use 'connect_server'")
        return None

def disconnect_server():
    global CLIENT_SOCKET
    if CLIENT_SOCKET is not None:
        CLIENT_SOCKET.close()
        CLIENT_SOCKET = None
        print("\nDisconnected from server")
    else:
        print("\nNo connection to close")
