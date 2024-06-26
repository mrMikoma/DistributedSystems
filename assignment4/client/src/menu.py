# Print main menu
def print_menu():
    print("\n1. Connect to server")
    print("2. Send private messages")
    print("3. Connect to chat channel")
    print("4. Disconnect from server")
    print("5. Exit program")
    return 0 

# TODO: Implement server call for getting available channels
# Print channel menu
def print_channel_menu():
    # Get channels from server
    channels = ["general", "random", "coding"]  # Hardcoded for now
    
    # Print channels
    print("\nChannels:")
    if not channels:
        print(" - No channels available")
    else: 
        for channel in channels:
            print(f" - {channel}")
    return 0
    
