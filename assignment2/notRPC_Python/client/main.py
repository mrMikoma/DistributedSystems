import lib

# Simple command line interface for the client
def main():
    while True:
        print("\n1. Add Note")
        print("2. Get Notes")
        print("3. Exit")
        choice = input("Select an option: ")

        if choice == '1':
            topic = input("Enter topic: ")
            text = input("Enter text: ")
            print("Adding note...")
            print(topic, text)     
            lib.addNote(topic, text)
            print("Note added successfully")
        elif choice == '2':
            topic = input("Enter topic to retrieve notes: ")
            print("Retrieving notes...")
            print(topic)            
            notes = lib.getNotes(topic)
            lib.printNotes(notes)            
            print("Notes retrieved successfully")
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
            
    return 0

if __name__ == "__main__":
    main()