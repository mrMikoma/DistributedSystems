import grpc
import time
from concurrent import futures

import chat_pb2
import chat_pb2_grpc

###
# References:
# https://grpc.io/docs/languages/python/basics/
#
###

# CONSTANTS
MAX_WORKERS = 10


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
            if request.message == "":
                return chat_pb2.Status(success=False, message="Message cannot be empty")

            # Send message to the user
            #users[request.recipient_id].add(request.message)

            #print("Viestit: " + users[request.recipient_id])  # Debug

            # Return status
            return chat_pb2.Status(success=True, message="Message sent successfully")
        except Exception as e:
            print(e)
            return chat_pb2.Status(success=False, message="Error occurred")
        
    
    def GetPrivateMessages(self, request, context):
        print("GetPrivateMessages") # Debug
        
        try:
            # Check if the user exists
            if request.user_id not in users:
                return chat_pb2.Messages()
            
            # Return messages
            return chat_pb2.Messages(messages=users[request.user_id])
        except Exception as e:
            print(e)
            return chat_pb2.Messages()
        
        
        # Return messages
        return chat_pb2.Message()
       
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