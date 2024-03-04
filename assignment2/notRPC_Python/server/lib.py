import xml.etree.ElementTree as ET
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import json

###
# Documentation used:
# https://docs.python.org/3/library/xml.etree.elementtree.html
# https://docs.python.org/3/library/json.html
# https://docs.python.org/3/library/http.server.html
# https://docs.python.org/3/library/datetime.html
# https://docs.python.org/3/library/socketserver.html
###

# Global variables
HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432        # The port used by the server
DB_FILE = "db.xml"  # The file to store notes

# Function to load the database file
def loadDB():
    try:
        tree = ET.parse(DB_FILE)
        root = tree.getroot()
        return tree, root
    except FileNotFoundError:
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
    timestamp = datetime.now().strftime('%m/%d/%y - %H:%M:%S')

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
    return

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

    # Return the notes
    return {'notes': notes}

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)

        # Define paths
        if self.path == '/add_note':
            # Parse data
            topic = data['topic']
            text = data['text']
            
            # Add note
            addNote(topic, text)
            
            # Send response
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Note added successfully")
        elif self.path == '/get_notes':
            # Parse data
            topic = data['topic']
            
            # Get notes
            notes = getNotes(topic)
            
            # Send response
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(notes).encode())
        else:
            # Send response if path not found
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")

# Function to run the server
def run(server_class=ThreadedHTTPServer, handler_class=SimpleHTTPRequestHandler, port=PORT):
    server_address = ('', port)
    httpd = ThreadedHTTPServer(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()

if __name__ == '__main__':
    run()