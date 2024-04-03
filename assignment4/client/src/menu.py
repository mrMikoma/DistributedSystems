# Print main menu
def printMenu():
    print("\n1. Connect to server")
    print("2. Send private message")
    print("3. See private messages")
    print("4. Connect to chat channel")
    print("5. Disconnect from server")
    print("6. Exit program")
    return 0 

# TODO: Implement rpc for getting channels
# Print channel menu
def printChannelMenu(chennels):
    for channel in chennels:
        printf(f"{channel}")
    return 0
    