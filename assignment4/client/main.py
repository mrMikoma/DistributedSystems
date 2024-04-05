from src.menu import *
from src.connect import *
from src.chatPrivate import *
from src.chatChannel import *
import sys

def main():
    print("\n###########################")
    print("Welcome to the chat client!")
    print("###########################")
    
    # Ask for the username
    USER_ID = input("\nEnter your username: ")
    
    # Initial server connection
    connect_server(USER_ID)
    
    while True:
        print_menu()
        option = input("Enter an option: ")
        if option == "1":
            connect_server(USER_ID)
        elif option == "2":
            connect_chat_private(USER_ID)
        elif option == "3":
            print_channel_menu()
            connect_chat_channel(USER_ID)
        elif option == "4":
            disconnect_server()
        elif option == "5":
            disconnect_server()
            break
        else:
            print("Invalid option. Please try again.")
    
    print("\nGoodbye!")
    sys.exit(0)
    return 0

main()
