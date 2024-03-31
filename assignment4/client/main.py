from src.menu import *
from src.connect import *
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
    
    while True:
        printMenu()
        option = input("Enter an option: ")
        if option == "1":
            connectServer()
        elif option == "2":
            sendPrivateMessage()
        elif option == "3":
            seePrivateMessages()
        elif option == "4":
            connectToChatChannel()
        elif option == "5":
            disconnectServer()
        elif option == "6":
            print("Exiting program...")
            break
        else:
            print("Invalid option. Please try again.")
    
    return 0

main()
