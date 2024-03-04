import xmlrpc.client

###
# Documentation used:
# - https://docs.python.org/3/library/xmlrpc.client.html#module-xmlrpc.client
###

# Global variables
SERVER_URL = "http://127.0.0.1:65432"  # URL of the server
SERVER = None                          # The server object

### NOTES FUNCTIONS ###

# Function to add a note
def addNote(topic, text):
    # Validate input
    if not topic or not text:
        return "Invalid input"
    elif len(topic) > 100 or len(text) > 1000:
        return "Input too long"
    
    # Add note to the server
    req = SERVER.addNote(topic, text)
    
    # Return the response
    return req

# Function to retrieve notes
def getNotes(topic):
    # Validate input
    if not topic:
        return "Invalid input"
    elif len(topic) > 100:
        return "Input too long"
    
    # Get notes from the server
    notes = SERVER.getNotes(topic)

    # Return the response
    return notes

# Function to print notes
def printNotes(notes):
    # Print the notes
    for note in notes['notes']:
        print(f"\n{note['text']}\n{note['timestamp']}")
        print("--------------------")    
    return

### WIKIPEDIA FUNCTIONS ###

# Function to query Wikipedia
def queryWikipedia(topic):
    # Validate input
    if not topic:
        return "Invalid input"
    elif len(topic) > 100:
        return "Input too long"
    
    # Query Wikipedia
    data = SERVER.queryWikipedia(topic)

    # Return the response
    return data

# Function to print the Wikipedia data
def printData(results):
    # Print the results with index number
    index = 0
    for result in results:
        print("Index:", index)
        print("Title:", result['title'])
        print("Link:", result['link'])
        print()
        index += 1
    return

# Function to run the client
def run(server_url=SERVER_URL):
    # Create the server object
    global SERVER
    SERVER = xmlrpc.client.ServerProxy(server_url)
    return