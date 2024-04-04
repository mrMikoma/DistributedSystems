from src.connect import *
import socket
import threading
import json
import time

### References:
# - https://docs.python.org/3.12/library/socket.html
# - https://docs.python.org/3.12/library/threading.html
# - https://docs.python.org/3.12/library/time.html
###

# Receive messages from the channel
def receive_messages(client_socket):
    while True:
        try:
            # Receive message from the server
            data = client_socket.recv(1024).decode()
            if not data:
                print("Server connection closed.")
                break
            
            #print(data) # Debug

            # Parse the message
            message_dict = json.loads(data)
            
            # Handle different message types
            if message_dict['type'] == 'channel':
                if message_dict['action'] == 'message':
                # Parse the timestamp
                    timestamp = time.localtime(message_dict['timestamp'])
                    message_dict['timestamp'] = time.strftime("%H:%M:%S", timestamp)
                    print(f"[{message_dict['timestamp']}] {message_dict['sender_id']}: {message_dict['content']}")
                else:
                    print(f"Unknown channel action: {message_dict['action']}")
            elif message_dict['type'] == 'private':
                print(f"This feature is not implemented yet.")
            else:
                print(f"Unknown message type: {message_dict['type']}")

        except (ConnectionError, json.JSONDecodeError) as e:
            print(f"Error receiving messages: {e}")
            break
    
    return 0

# Send messages to the channel 
def send_message(client_socket, channel_id, sender_id):
    while True:
        # Get user input
        content = input()  # Get user input
        
        # Handle empty message
        if not content:
            continue
        
        # Handle exit command
        if content.lower() == 'exit':
            break

        # Create message object
        message = json.dumps({
            "type": "channel",
            "action": "message",
            "channel_id": channel_id,
            "sender_id": sender_id,
            "content": content,
        })

        # Send message to the server
        client_socket.sendall(message.encode())
        
    return 0

def manage_channel(client_socket, channel_id, action):
    # Check if the action is valid
    if action not in ("join", "leave"):
        raise ValueError("Invalid action. Must be 'join' or 'leave'.")

    # Send the message to the server
    message = json.dumps({
        "type": "channel",
        "action": action,
        "channel_id": channel_id,
    })
    client_socket.sendall(message.encode())

    return 0 

def connect_chat_channel(user_id):
    # Ask for the channel ID
    channel_id = input("Enter the channel name you want to connect to: ")
    
    # Get socket connection
    client_socket = get_client()
    
    # Connect to the channel
    manage_channel(client_socket, channel_id, "join")
    
    # Print information about the channel
    print(f"\nConnected to channel {channel_id}")
    print("Type 'exit' to leave the channel\n")
    
    # Start thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, ))
    receive_thread.start()

    # Send thread to send messages
    send_thread = threading.Thread(target=send_message, args=(client_socket, channel_id, user_id))
    send_thread.start() 
    send_thread.join() # Wait for the send thread to finish

    # Disconnect from the channel
    manage_channel(client_socket, channel_id, "leave") # Leave the channel
    
    # Return
    print("\nDisconnected from channel")
    return 0