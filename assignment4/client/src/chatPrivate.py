from src.connectRPC import *
import chat_pb2
import chat_pb2_grpc
from datetime import datetime

###
# TODO:
# - Fix query for private messages
# -
###

def sendPrivateMessage(user_id):
    # Ask for the username of the person to send the message to
    recipient_id = input("Enter the username of the person you want to send a message to: ")
    content = input("Enter the message you want to send: ")
    
    # Create a channel stub
    try:
        client = getClient()
        stub = chat_pb2_grpc.ChatServiceStub(client)
    except Exception as e:
        print("Error: Could not send message to server")
        print(e)
        return 1
    
    # Send the message to the server
    request = chat_pb2.PrivateMessage(
        sender_id=user_id,
        recipient_id=recipient_id,
        content=content
    )
    
    # Handle the response
    response = stub.SendPrivateMessage(request)
    if response.success:
        print("Message sent successfully") # Debug
        return 0
    else:
        print("Error: " + response.message)
        return 1

def getPrivateMessages(user_id):
    # Ask for the username of the person to get the messages from
    recipient_id = input("Enter username of the person you want to get messages from: ")
    
    # Cet RPC client
    client = getClient()
    if client == 1:
        return 1
    
    # Create a channel stub
    stub = chat_pb2_grpc.ChatServiceStub(client)
    
    request = chat_pb2.PrivateMessageRequest(
        sender_id=user_id, 
        recipient_id=recipient_id
    )
    messages = stub.GetPrivateMessages(request)

    # Collect messages with timestamps
    message_list = [(message.timestamp, message.user_id, message.content) for message in messages]
    
    # If no messages are found, print a message and return
    if not message_list:
        print("\nNo messages found")
        return 0

    # Sort by timestamp in ascending order
    message_list.sort(key=lambda item: item[0])

    # Print messages with formatted timestamps
    print("")
    for timestamp, user_id, content in message_list:
        dt_object = datetime.fromtimestamp(timestamp)
        print(f"[{dt_object.strftime('%Y-%m-%d %H:%M')}] {user_id}: {content}") 
    
    return 0

