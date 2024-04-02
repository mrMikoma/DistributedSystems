import grpc

# CONSTANTS
CLIENT = None

def connectServer():
    # Asks for the server IP
    redis_host = input("Enter the server IP: ")
    
    # Create a connection to the server if it does not exist
    global CLIENT
    if CLIENT is None:
        try:
            CLIENT = grpc.insecure_channel(redis_host + ':50051')
            print("\nConnection established")
            return 0
        except Exception as e:
            print("\nError: Could not connect to server")
            print(e)
            return 1
        return 0
    else:
        print("\nConnection already exists")
        return 1
    
def getClient():
    if CLIENT is not None:
        return CLIENT
    else:
        print("\nNo connection to server")
        return 1

def disconnectServer():
    # Close the connection to the server
    global CLIENT
    if CLIENT is not None:
        CLIENT.close()
        CLIENT = None
        print("\nDisconnected from server")
        return 0
    else:
        print("\nNo connection to close")
        return 1
   