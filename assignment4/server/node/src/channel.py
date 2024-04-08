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

# Global variables
channels = {    
    "general": set(),
    "coding": set(),
    "random": set()
}

class Channel:
    def __init__(self):
        pass
    
    # Store the message in Redis
    @staticmethod
    def store_message(channel_id, message_dict):
        try:
            # Connect to Redis
            redis_client = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379, db=0, password=os.getenv('REDIS_PASSWORD'))
            
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
    @staticmethod
    def broadcast_recent_messages(channel_id, new_client_conn):
        # Connect to Redis
        redis_client = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379, db=0, password=os.getenv('REDIS_PASSWORD'))
        
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
    
    # Broadcast a message to all users in a channel
    @staticmethod
    def broadcast_to_channel(clients, channel_id, message_dict):
        # Broadcast the message to all users in the channel
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

    # Join a channel
    @staticmethod
    def join_channel(client_user_id, channel_id):
        if channel_id in channels: 
            channels[channel_id].add(client_user_id)
            print(f"User '{client_user_id}' joined channel '{channel_id}'.")
        else:
            print(f"Channel '{channel_id}' does not exist.") 

    # Leave a channel
    @staticmethod
    def leave_channel(client_user_id, channel_id):
        if channel_id in channels: 
            if client_user_id in channels[channel_id]:
                channels[channel_id].remove(client_user_id)
            else:
                print(f"User '{client_user_id}' is not in channel '{channel_id}'.") 
        else:
            print(f"Channel '{channel_id}' does not exist.")

### Helper functions ###
# Format the message to be sent to the client
def format_channel_message(message_dict, timestamp):
    message_dict = {
        "type": "channel",
        "action": "message",
        "sender_id": message_dict["sender_id"],
        "content": message_dict["content"],
        "timestamp": int(timestamp)
    }
    return json.dumps(message_dict) + '\n'  
