import xmlrpc.server
import xml.etree.ElementTree as ET
from datetime import datetime
import requests

###
# Documentation used:
# - https://docs.python.org/3/library/xml.etree.elementtree.html
# - https://docs.python.org/3/library/xmlrpc.server.html#module-xmlrpc.server
# - https://docs.python.org/3/library/datetime.html
# - https://requests.readthedocs.io/en/latest/
# - https://www.mediawiki.org/wiki/API:Opensearch
###

# Global variables
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432        # The port used by the server
DB_FILE = "db.xml"  # The file to store notes

# Function to load the database file
def loadDB():
    try:
        # Load the database file
        tree = ET.parse(DB_FILE)
        root = tree.getroot()
        return tree, root
    except FileNotFoundError:
        # Create the database file if
        root = ET.Element("data")
        tree = ET.ElementTree(root)
        tree.write(DB_FILE)
        return tree, root

# Function to save the database file
def saveDB(tree):
    tree.write(DB_FILE)

# Function to add a note
def addNote(topic, text):
    # Declare variables
    tree, root = loadDB()
    timestamp = datetime.now().strftime('%d/%m/%y - %H:%M:%S')

    # Check if the topic exists, if not create it
    topic_elem = root.find(f"./topic[@name='{topic}']")
    if topic_elem is None:
        topic_elem = ET.SubElement(root, 'topic', {'name': topic})

    # Create note element
    note_elem = ET.SubElement(topic_elem, 'note')
    note_elem.set('name', f'Note {len(topic_elem.findall("note")) + 1}')
    
    # Add note elements
    text_elem = ET.SubElement(note_elem, 'text')
    text_elem.text = text
    timestamp_elem = ET.SubElement(note_elem, 'timestamp')
    timestamp_elem.text = timestamp

    # Save the database and return
    saveDB(tree)
    return "Note added successfully"

# Function to get notes
def getNotes(topic):
    # Declare variables
    notes = []
    tree, _ = loadDB()

    # Find the topic element
    topic_elem = tree.find(f"./topic[@name='{topic}']")
    if topic_elem is None:
        return "Topic not found"
    
    # Parse notes from the topic
    for note_elem in topic_elem.findall('note'):
        note = {
            'text': note_elem.find('text').text,
            'timestamp': note_elem.find('timestamp').text
        }
        notes.append(note)

    # Return the notes as JSON
    return {'notes': notes}

# Function to query Wikipedia
def queryWikipedia(topic):
    # Declare variables
    session = requests.Session()
    wikipedia_url = "https://en.wikipedia.org/w/api.php"
    params = {
    "action": "opensearch",
    "namespace": "0",
    "search": topic,
    "limit": "5",
    "format": "json"
    }

    # Make the request
    response = session.get(url=wikipedia_url, params=params)
    
    # Extract the response
    data = response.json()
    topic = data[0]
    titles = data[1]
    links = data[3]

    # Extract the information from the lists
    results = []
    for i in range(len(titles)):
        result = {}
        result['title'] = titles[i]
        result['link'] = links[i]
        results.append(result)

    # Return the response
    return results

# Function to run the server
def run(host=HOST, port=PORT):
    # Create the server object
    server = xmlrpc.server.SimpleXMLRPCServer((host, port))
    
    # Register the functions
    server.register_function(addNote, 'addNote')
    server.register_function(getNotes, 'getNotes')
    server.register_function(queryWikipedia, 'queryWikipedia')
    
    # Start the server
    print(f"Starting XML-RPC server on port {port}...")
    server.serve_forever()
    