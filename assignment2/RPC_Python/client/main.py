import lib

# Simple command line interface for the client
def main():
    lib.run()   # Declare the server
    
    # Main loop
    while True:
        # Print the menu
        print("\n1. Add Note")
        print("2. Get Notes")
        print("3. Get Wikipedia Query")
        print("4. Exit")
        
        # Get the user's choice
        choice = input("Select an option: ")

        if choice == '1':
            # Ask for input
            topic = input("Enter topic: ")
            text = input("Enter text: ")
            
            # Handle the input
            print("Adding note...")
            print(topic, text)     
            lib.addNote(topic, text)
            print("Note added successfully")
        elif choice == '2':
            # Ask for input
            topic = input("Enter topic to retrieve notes: ")
            
            # Handle the input
            print("Retrieving notes...")
            print(topic)            
            notes = lib.getNotes(topic)
            
            # Print the notes
            lib.printNotes(notes)            
            print("Notes retrieved successfully")
        elif choice == '3':
            # Ask for input
            topic = input("Enter Wikipedia topic to query: ")
            
            # Handle the input
            print("Retrieving Wikipedia query...")
            print(topic)            
            results = lib.queryWikipedia(topic)
            
            # Print the results
            lib.printData(results)
            print("Data retrieved successfully")     

            # Ask for input and validate
            index = int(input("Enter which index to add to the topic: "))
            selected_result = results[index] if 0 <= index < len(results) else None

            if selected_result:
                text = selected_result['title'] + " " + selected_result['link']
                print(text) # debug
                lib.addNote(topic, text)   
                print("Note added successfully")
            else:
                print("Invalid index entered")
        elif choice == '4':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")
            
    return 0

if __name__ == "__main__":
    main()      # Run the client