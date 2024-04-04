from src.channel import Channel
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
        print("Private messages not supported")
        return 1
    elif message_dict['type'] == 'system': # Handle system messages
        print("System messages not supported")
        return 1
    else: # Handle other message types
        print("Message type not supported")
        return 1
    return 0

def get_clients():
    return clients

# Server function
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


############################# DEPRECATED ############################# 
"""
class ChatServiceServicer(chat_pb2_grpc.ChatServiceServicer):
    def SendPrivateMessage(self, request, context):
        print("SendPrivateMessage") # Debug
        
        try:
            # Check if the sender and recipient are the same
            if request.sender_id == request.recipient_id:
                return chat_pb2.Status(success=False, message="Sender and recipient cannot be the same")
            
            # Check if the message is empty
            if request.content == "":
                return chat_pb2.Status(success=False, message="Message cannot be empty")
            
            # Connect to Redis
            redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, password=os.getenv('REDIS_PASSWORD'))
            #redis_client.flushall() # Debug (Clear all keys in Redis)
            
            # Store the message in Redis
            redis_key = f"private_messages:{request.recipient_id}"  # Key format: private_messages:<recipient_id>
            redis_object = json.dumps({ # JSON object to store in Redis
                "sender_id": request.sender_id,
                "content": request.content,
                "timestamp": int(time.time())
            })
            redis_client.rpush(redis_key, redis_object) # Append the message to the Redis list

            # Return status
            return chat_pb2.Status(success=True, message="Message sent successfully")
        except Exception as e:
            print(e)  # Debug
            return chat_pb2.Status(success=False, message="Error occurred")

    def GetPrivateMessages(self, request, context):
        print("GetPrivateMessages")  

        try:
            # Connect to Redis
            redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, password=os.getenv('REDIS_PASSWORD'))

            # Construct the Redis keys for both directions of the conversation
            key1 = f"private_messages:{request.sender_id}"  # Where the user is the recipient
            key2 = f"private_messages:{request.recipient_id}" # Where the user is the sender

            # Fetch messages from Redis using LRANGE
            messages = redis_client.lrange(key1, 0, -1) + redis_client.lrange(key2, 0, -1)
            
            # Parse messages only between the sender and recipient
            #messages = [message for message in messages if json.loads(message)["user_id"] == request.sender_id or json.loads(message)["user_id"] == request.recipient_id]
            messages = [message for message in messages if json.loads(message)["sender_id"] in {request.sender_id, request.recipient_id}]

            # Yield individual messages
            for message_json in messages:
                # Parse the JSON object
                message_dict = json.loads(message_json)
                
                # Yield the message
                yield chat_pb2.Message(sender_id=message_dict["sender_id"], content=message_dict["content"], timestamp=message_dict["timestamp"]) 

        except Exception as e:
            print(e) 
            return chat_pb2.Status(success=False, message="Error occurred")
        
    def SendChannelMessage(self, request, context):
        print("SendChannelMessage")
        
        try: 
            # Check if the channel exists
            if request.channel_id not in CHANNELS:
                return chat_pb2.Status(success=False, message="Channel does not exist")
            
            # Check if the message is empty
            if request.content == "":
                return chat_pb2.Status(success=False, message="Message cannot be empty")
            
            # Connect to Redis
            redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, password=os.getenv('REDIS_PASSWORD'))
            #redis_client.flushall() # Debug (Clear all keys in Redis)
            
            # Store the message in Redis
            redis_key = f"channel_messages:{request.channel_id}"  # Key format: channel_messages:<channel_id>
            redis_object = json.dumps({ # JSON object to store in Redis
                "sender_id": request.sender_id,
                "content": request.content,
                "timestamp": int(time.time())
            })
            # ZADD for Sorted Set to store messages in order of timestamp
            redis_client.zadd(redis_key, {redis_object: int(time.time())}) # Append the message to the Redis sorted set
            
            # Return status
            return chat_pb2.Status(success=True, message="Message sent successfully")
        
        except Exception as e:
            print(e)
            return chat_pb2.Status(success=False, message="Error occurred")
        
    def GetChannelMessages(self, request, context):
            print("GetChannelMessages")  

            try:
                # Declare last timestamp
                last_timestamp = 0
                
                # Connect to Redis
                redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, password=os.getenv('REDIS_PASSWORD'))

                # Construct the Redis key for the channel
                key = f"channel_messages:{request.channel_id}"  # Key format: channel_messages:<channel_id>
                
                # Initial fetch
                messages = redis_client.zrangebyscore(key, last_timestamp, '+inf', withscores=True)
                
                # Yield initially fetched messages
                for message, timestamp in messages: 
                    # Yield the message
                    message_dict = json.loads(message)
                    yield chat_pb2.Message(sender_id=message_dict["sender_id"], content=message_dict["content"], timestamp=int(timestamp))
                    
                    # Store the last timestamp
                    last_timestamp = timestamp

                # Continuous streaming loop
                while True:
                    # Fetch messages from Redis using ZRANGEBYSCORE
                    messages = redis_client.zrangebyscore(key, last_timestamp + 1, '+inf', withscores=True)  

                    # Yield messages
                    for message, timestamp in messages:
                        message_dict = json.loads(message)
                        yield chat_pb2.Message(sender_id=message_dict["sender_id"], content=message_dict["content"], timestamp=int(timestamp))
                        
                        # Store the last timestamp
                        last_timestamp = timestamp

                    time.sleep(1)  # Sleep for 1 second before fetching the next message
                    
                # Return status
                return chat_pb2.Status(success=True, message="Channel connection closed")

            except Exception as e:
                print(e) 
                return chat_pb2.Status(success=False, message="Error occurred")
"""
############################# DEPRECATED #############################  