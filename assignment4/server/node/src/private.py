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
chats = {}    

class Private:
    def __init__(self):
        pass
    
    # Store the message in Redis
    @staticmethod
    def store_message(client_user_id, message_dict):
        try:
            # Connect to Redis
            redis_client = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379, db=0, password=os.getenv('REDIS_PASSWORD'))
            
            # Store the message in Redis
            redis_key = format_private_key(client_user_id, message_dict['recipient_id'])  # Key format: private:<user_id1>:<user_id2>
            redis_object = json.dumps({ # JSON object to store in Redis
                "sender_id": message_dict['sender_id'],
                "recipient_id": message_dict['recipient_id'],
                "content": message_dict['content'],
                "timestamp": int(time.time())
            })
            # ZADD for Sorted Set to store messages in order of timestamp
            redis_client.zadd(redis_key, {redis_object: int(time.time())}) # Append the message to the Redis sorted set
        except Exception as e:
            print(f"Error occurred while storing message in Redis: {e}")
            return 1
        
        print(f"Message stored in Redis for user '{client_user_id}'")
        return 0
        
    # Broadcast recent messages to a new client
    @staticmethod
    def broadcast_recent_messages(client_user_id, new_client_conn, message_dict):
        # Connect to Redis
        redis_client = redis.Redis(host=os.getenv('REDIS_HOST'), port=6379, db=0, password=os.getenv('REDIS_PASSWORD'))
        
        # Timestamp for 1 day ago 
        time_ago = int(time.time()) - 86400  

        # Retrieve recent messages (those with timestamps greater than 'time_ago')
        redis_key = format_private_key(client_user_id, message_dict['recipient_id'])
        recent_messages = redis_client.zrangebyscore(redis_key, time_ago, '+inf', withscores=True)
        
        #redis_client.flushall() # Debug (Clear all keys in Redis)
    
        # Broadcast retrieved messages
        for message, timestamp in recent_messages:
            # Decode the message
            message_dict = json.loads(message)
            message_to_send = format_private_message(message_dict, timestamp)
            
            # Broadcast to the new client only
            try:
                new_client_conn.sendall((message_to_send + '\n').encode())
                time.sleep(0.1)  # Send messages with a delay to avoid congestion
            except Exception as e: 
                print(f"Error occurred while sending message to new client: {e}")
                new_client_conn.close()
                pass
    
    # Broadcast a message to all users in a chat
    @staticmethod
    def broadcast_to_user(clients, message_dict):
        # Format the private chat key
        chat_key = format_private_key(message_dict['sender_id'], message_dict['recipient_id'])
        
        # Check if the chat exists
        if chat_key in chats:
            for user_id in chats[chat_key]:
                if user_id != message_dict['sender_id']:
                    # Get the user's connection
                    user_conn = clients[user_id]
                    
                    # Send the message to the user
                    try:
                        user_conn.sendall(format_private_message(message_dict, int(time.time())).encode())
                    except Exception as e:
                        print(f"Error occurred while sending message to user '{user_id}': {e}")
                        user_conn.close()
                        pass
        else:
            print(f"Chat does not exist.")
        
    # Join a chat
    @staticmethod
    def join_chat(client_user_id, message_dict):
        # Format the private chat key
        chat_key = format_private_key(client_user_id, message_dict['recipient_id'])
        
        # Check if the chat exists
        if chat_key in chats: # Add the user to the chat if it exists
            if client_user_id not in chats[chat_key]:
                chats[chat_key].add(client_user_id)
                print(f"User '{client_user_id}' joined the chat with '{message_dict['recipient_id']}'.")
            else:
                print(f"User '{client_user_id}' is already in the chat.")
        else: # Create a new chat if it does not exist
            chats[chat_key] = set([client_user_id])
            print(f"User '{client_user_id}' started a chat with '{message_dict['recipient_id']}'.")
        return 0

    # Leave a chat
    @staticmethod
    def leave_chat(client_user_id, message_dict):
        # Format the private chat key
        chat_key = format_private_key(client_user_id, message_dict['recipient_id'])
        
        # Check if the chat exists
        if chat_key in chats:
            if client_user_id in chats[chat_key]:
                chats[chat_key].remove(client_user_id)
                print(f"User '{client_user_id}' left the chat.")
            else:
                print(f"User '{client_user_id}' is not in the chat.")
        else:
            print(f"Chat does not exist.")
            
        # If the chat is empty, remove it
        if len(chats[chat_key]) == 0:
            del chats[chat_key]
            print(f"Chat '{chat_key}' is empty and has been removed.")
        
        return 0

### Helper functions ###
# Format the message to be sent to the client
def format_private_message(message_dict, timestamp):
    message_dict = {
        "type": "private",
        "action": "message",
        "sender_id": message_dict["sender_id"],
        "content": message_dict["content"],
        "timestamp": int(timestamp)
    }
    return json.dumps(message_dict) + '\n'  

# Format the private chat key for Redis with alphabetical order
def format_private_key(user_id1, user_id2):
    # Sort the user IDs alphabetically and concatenate them to form the key
    sorted_user_ids = sorted([user_id1, user_id2])
    return f"private:{sorted_user_ids[0]}:{sorted_user_ids[1]}"  # Key format: private:<user_id1>:<user_id2>
