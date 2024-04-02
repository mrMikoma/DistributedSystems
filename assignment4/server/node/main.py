import grpc
import time
import redis
from concurrent import futures
import os
import json
from dotenv import load_dotenv

import chat_pb2
import chat_pb2_grpc

###
# References:
# https://grpc.io/docs/languages/python/basics/
#
###

# CONSTANTS
MAX_WORKERS = 10
REDIS_HOST = 'localhost'

load_dotenv()  # Load environment variables from .env

# Maintain active users, channels, and their subscriptions
users = {}
channels = {} 

class ChatServiceServicer(chat_pb2_grpc.ChatServiceServicer):
    def SendPrivateMessage(self, request, context):
        try:
            print("SendPrivateMessage") # Debug

            # Check if the users exist
            if request.sender_id not in users or request.recipient_id not in users:
                return chat_pb2.Status(success=False, message="User does not exist")
            
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
                "user_id": request.sender_id,
                "content": request.content,
                "timestamp": int(time.time())
            })
            redis_client.rpush(redis_key, redis_object) # Append the message to the Redis list

            # Return status
            return chat_pb2.Status(success=True, message="Message sent successfully")
        except Exception as e:
            print(e)  # Debug
            return chat_pb2.Status(success=False, message="Error occurred")
        
    
    import redis

    def GetPrivateMessages(self, request, context):
        print("GetPrivateMessages")  

        try:
            # Connect to Redis
            redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0, password=os.getenv('REDIS_PASSWORD'))

            # Check if the users exists
            if request.sender_id not in users and request.recipient_id not in users: 
                return chat_pb2.Status(success=False, message="User does not exist")

            # Construct the Redis keys for both directions of the conversation
            key1 = f"private_messages:{request.sender_id}"  # Where the user is the recipient
            key2 = f"private_messages:{request.recipient_id}" # Where the user is the sender

            # Fetch messages from Redis using LRANGE
            messages = redis_client.lrange(key1, 0, -1) + redis_client.lrange(key2, 0, -1)
            
            # Parse messages only between the sender and recipient
            messages = [message for message in messages if json.loads(message)["user_id"] == request.sender_id or json.loads(message)["user_id"] == request.recipient_id]

            # Yield individual messages
            for message_json in messages:
                # Parse the JSON object
                message_dict = json.loads(message_json)
                
                # Yield the message
                yield chat_pb2.Message(user_id=message_dict["user_id"], content=message_dict["content"], timestamp=message_dict["timestamp"]) 

        except Exception as e:
            print(e) 
            return chat_pb2.Status(success=False, message="Error occurred")

# Function for initializing data structures     
def initialize():
    # Initialize users
    users["user1"] = set()
    users["user2"] = set()
    users["user3"] = set()
    
    # Initialize channels
    channels["general"] = set()
    channels["random"] = set()
    channels["private"] = set()
    return 0

def serve():
    # Initialize data structures
    initialize()
    
    # Initialize the server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    chat_pb2_grpc.add_ChatServiceServicer_to_server(ChatServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    try:
        while True:
            print("Server is running...")
            time.sleep(86400)  # One day
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()