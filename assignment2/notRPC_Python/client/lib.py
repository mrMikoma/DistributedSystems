import json
import requests

###
# Documentation used:
# https://docs.python.org/3/library/json.html
# https://requests.readthedocs.io/en/latest/
###

# Global variables
SERVER_URL = "http://127.0.0.1:65432"  # URL of the server

# Function to add a note
def addNote(topic, text):
    # Validate input
    if not topic or not text:
        return "Invalid input"
    elif len(topic) > 100 or len(text) > 1000:
        return "Input too long"
    
    # Declare variables
    url = SERVER_URL + "/add_note"
    data = json.dumps({"topic": topic, "text": text})
    
    # Send the request
    req = requests.post(url, data=data, headers={'Content-Type': 'application/json'})
    
    # Return the response
    return req

# Function to retrieve notes
def getNotes(topic):
    # Validate input
    if not topic:
        return "Invalid input"
    elif len(topic) > 100:
        return "Input too long"
    
    # Declare variables
    url = SERVER_URL + "/get_notes"
    data = json.dumps({"topic": topic})
    
    # Send the request
    req = requests.post(url, data=data, headers={'Content-Type': 'application/json'})
    
    # Return the response
    return req.json()

# Function to print notes
def printNotes(notes):
    # Print the notes
    for note in notes['notes']:
        print(f"\n{note['text']}\n{note['timestamp']}")
        print("--------------------")
            
    return