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
            if message_dict['type'] == 'private':
                if message_dict['action'] == 'message':
                # Parse the timestamp
                    timestamp = time.localtime(message_dict['timestamp'])
                    message_dict['timestamp'] = time.strftime("%H:%M:%S", timestamp)
                    print(f"[{message_dict['timestamp']}] {message_dict['sender_id']}: {message_dict['content']}")
                else:
                    print(f"Unknown channel action: {message_dict['action']}")
            else:
                print(f"Unknown message type: {message_dict['type']}")

        except (ConnectionError, json.JSONDecodeError) as e:
            print(f"Error receiving messages: {e}")
            break
    
    return 0

# Send messages to the channel 
def send_message(client_socket, sender_id, recipient_id):
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
            "type": "private",
            "action": "message",
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "content": content,
        })

        # Send message to the server
        client_socket.sendall(message.encode())
        
    return 0

def manage_private(client_socket, user_id, recipient_id, action):
    # Check if the action is valid
    if action not in ("join", "leave"):
        raise ValueError("Invalid action. Must be 'join' or 'leave'.")

    # Send the message to the server
    message = json.dumps({
        "type": "private",
        "action": action,
        "sender_id": user_id,
        "recipient_id": recipient_id,
    })
    client_socket.sendall(message.encode())

    return 0 

def connect_chat_private(user_id):
    # Ask for the recipient ID
    recipient_id = input("Enter recipient name: ")
    
    # Get socket connection
    client_socket = get_client()
    
    # Connect to the channel
    manage_private(client_socket, user_id, recipient_id, "join")
    
    # Print information about the channel
    print(f"\nConnected to private chat with {recipient_id}")
    print("Type 'exit' to leave the chat\n")
    
    # Start thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket, ))
    receive_thread.start()

    # Send thread to send messages
    send_thread = threading.Thread(target=send_message, args=(client_socket, user_id, recipient_id))
    send_thread.start() 
    send_thread.join() # Wait for the send thread to finish

    # Disconnect from the channel
    manage_private(client_socket, user_id, recipient_id, "leave") # Leave the channel
    
    # Return
    print("\nDisconnected from channel")
    return 0