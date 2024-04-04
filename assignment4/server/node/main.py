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
# - https://redis.io/docs/connect/clients/python/
# - 
###

# CONSTANTS (Environment)
load_dotenv()  # Load environment variables from .env   
REDIS_HOST = 'localhost'
HOST = 'localhost'
PORT = 65432

# Global variables
channels = {    
    "general": set(),
    "coding": set(),
    "random": set()
}
clients = {} # Dictionary to store connected clients

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
                join_channel(client_user_id, channel_id) # Join the channel
                broadcast_recent_messages(channel_id, clients[client_user_id]) # Broadcast recent messages to the new client
            elif message_dict.get('action') == 'leave':  # Check for 'leave' action
                leave_channel(client_user_id, channel_id)  # Leave the channel
            elif message_dict.get('action') == 'message':  # Check for 'message' action
                store_message(channel_id, message_dict) # Store the message in Redis
                broadcast_to_channel(channel_id, message_dict) # Broadcast the message to all clients
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

# Store the message in Redis
def store_message(channel_id, message_dict):
    try:
        # Connect to Redis
        redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, password=os.getenv('REDIS_PASSWORD'))
        
        # Store the message in Redis
        redis_key = f"channel_messages:{message_dict['channel_id']}"  # Key format: channel_messages:<channel_id>
        redis_object = json.dumps({ # JSON object to store in Redis
            "sender_id": message_dict['sender_id'],
            "content": message_dict['content'],
            "timestamp": int(time.time())
        })
        # ZADD for Sorted Set to store messages in order of timestamp
        redis_client.zadd(redis_key, {redis_object: int(time.time())}) # Append the message to the Redis sorted set
    except Exception as e:
        print(f"Error occurred while storing message in Redis: {e}")
        return 1
    
    print(f"Message stored in Redis for channel '{channel_id}'")
    return 0
    
# Broadcast recent messages to a new client
def broadcast_recent_messages(channel_id, new_client_conn):
    # Connect to Redis
    redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, password=os.getenv('REDIS_PASSWORD'))
    
    # Timestamp for 1 day ago 
    time_ago = int(time.time()) - 86400  

    # Retrieve recent messages (those with timestamps greater than 'time_ago')
    redis_key = f"channel_messages:{channel_id}"
    recent_messages = redis_client.zrangebyscore(redis_key, time_ago, '+inf', withscores=True)
    
    #redis_client.flushall() # Debug (Clear all keys in Redis)
 
    # Broadcast retrieved messages
    for message, timestamp in recent_messages:
        # Decode the message
        message_dict = json.loads(message)
        message_to_send = format_channel_message(message_dict, timestamp)
        
        # Broadcast to the new client only
        try:
            new_client_conn.sendall((message_to_send + '\n').encode())
            time.sleep(0.1)  # Send messages with a delay to avoid congestion
        except Exception as e: 
            print(f"Error occurred while sending message to new client: {e}")
            new_client_conn.close()
            pass
        
def broadcast_to_channel(channel_id, message_dict):
    if channel_id in channels:  # Check if the channel exists
        for user_id in channels[channel_id]:
            if user_id in clients:
                try:
                    clients[user_id].sendall((format_channel_message(message_dict, time.time())).encode())
                    time.sleep(0.1)  # Send messages with a delay to avoid congestion
                except Exception as e: 
                    print(f"Error occurred while broadcasting message to user '{user_id}': {e}")
                    clients[user_id].close()
                    pass
    else:
        print(f"Channel '{channel_id}' does not exist.")

def join_channel(client_user_id, channel_id):
    if channel_id in channels: 
        channels[channel_id].add(client_user_id)
        print(f"User '{client_user_id}' joined channel '{channel_id}'.")
    else:
        print(f"Channel '{channel_id}' does not exist.") 

def leave_channel(client_user_id, channel_id):
    if channel_id in channels: 
        if client_user_id in channels[channel_id]:
            channels[channel_id].remove(client_user_id)
        else:
            print(f"User '{client_user_id}' is not in channel '{channel_id}'.") 
    else:
        print(f"Channel '{channel_id}' does not exist.")
        
def format_channel_message(message_dict, timestamp):
    message_dict = {
        "type": "channel",
        "action": "message",
        "sender_id": message_dict["sender_id"],
        "content": message_dict["content"],
        "timestamp": int(timestamp)
    }
    return json.dumps(message_dict) + '\n'  

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