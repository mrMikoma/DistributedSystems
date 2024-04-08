from src.channel import Channel
from src.private import Private
import os
import socket
import threading
import redis
import time
import json
from dotenv import load_dotenv

###
# References:
# - https://docs.python.org/3.12/library/socket.html
# - https://docs.python.org/3.12/library/threading.html
# - 
###

# CONSTANTS (Environment)
load_dotenv()  # Load environment variables from .env   
HOST = 'localhost'
PORT = 65432

# Global variables
clients = {} # Dictionary to store connected clients
channels = {    
    "general": set(),
    "coding": set(),
    "random": set()
}

# Top level function to handle client connections   
def handle_client(conn, addr):
    print(f"Connected by {addr}")
    
    # Receive the username from the client
    client_user_id = conn.recv(1024).decode().strip()
    clients[client_user_id] = conn

    # Receive data from the client
    while True:
        try:
            # Receive data from the client
            data = conn.recv(1024)
            
            # Check if the data is empty
            if not data:
                break
            
            # Decode the data and process the message
            message_dict = json.loads(data.decode())
            process_message(client_user_id, message_dict)

        except (ConnectionError, json.JSONDecodeError) as e:
            print(f"Connection from {addr} closed with error: {e}")
            break  

    # Close the connection
    del clients[client_user_id]
    conn.close()
    return 0
    
# Process the message received from the client
def process_message(client_user_id, message_dict):
    # Handle different message types
    if message_dict['type'] == 'channel': # Handle channel messages
        if message_dict['channel_id'] in channels: # Check if the channel exists
            channel_id = message_dict['channel_id'] # Extract the channel ID
            if message_dict.get('action') == 'join':  # Check for 'join' action
                Channel.join_channel(client_user_id, channel_id) # Join the channel
                Channel.broadcast_recent_messages(channel_id, clients[client_user_id]) # Broadcast recent messages to the new client
            elif message_dict.get('action') == 'leave':  # Check for 'leave' action
                Channel.leave_channel(client_user_id, channel_id)  # Leave the channel
            elif message_dict.get('action') == 'message':  # Check for 'message' action
                Channel.store_message(channel_id, message_dict) # Store the message in Redis
                Channel.broadcast_to_channel(clients, channel_id, message_dict) # Broadcast the message to all clients
            else: # Handle unsupported actions
                print("Action not supported")
                return 1
        else: # Handle non-existent channels
            print(f"Channel '{message_dict['channel_id']}' does not exist.")
            return 1
    elif message_dict['type'] == 'private': # Handle private messages
        if message_dict.get('action') == 'join':  # Check for 'join' action
            Private.join_chat(client_user_id, message_dict) # Join the chat
            Private.broadcast_recent_messages(client_user_id, clients[client_user_id], message_dict) # Broadcast recent messages to the new client
        elif message_dict.get('action') == 'leave':  # Check for 'leave' action
            Private.leave_chat(client_user_id, message_dict) # Leave the chat
        elif message_dict.get('action') == 'message':
            Private.store_message(client_user_id, message_dict) # Store the message in Redis
            Private.broadcast_to_user(clients, message_dict) # Broadcast the message to the recipient
        else: # Handle unsupported actions
            print("Action not supported")
            return 1
    elif message_dict['type'] == 'system': # Handle system messages
        print("System messages not supported")
        return 1
    else: # Handle other message types
        print("Message type not supported")
        return 1
    return 0

# Main server function
def serve():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print("Server listening...")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            
    return 0

if __name__ == '__main__':
    serve()
