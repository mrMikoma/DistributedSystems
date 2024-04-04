from src.menu import *
from src.connectRPC import *
from src.chatPrivate import *
from src.chatChannel import *

###
# References:
# 
#
###

def main():
    print("\n###########################")
    print("Welcome to the chat client!")
    print("###########################")
    
    # Ask for the username
    USER_ID = input("\nEnter your username: ")
    
    # Initial server connection
    connectServer()
    
    while True:
        printMenu()
        option = input("Enter an option: ")
        if option == "1":
            connectServer()
        elif option == "2":
            sendPrivateMessage(USER_ID)
        elif option == "3":
            getPrivateMessages(USER_ID)
        elif option == "4":
            printChannelMenu() # create rpc for getting channels
            connectToChatChannel(USER_ID)
        elif option == "5":
            disconnectServer()
        elif option == "6":
            disconnectServer()
            break
        else:
            print("Invalid option. Please try again.")
    
    print("\nGoodbye!")
    return 0

main()
