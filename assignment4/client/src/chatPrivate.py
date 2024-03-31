
def sendPrivateMessage():
    print("Enter the username of the person you want to send a message to:")
    username = input()
    print("Enter the message you want to send:")
    message = input()
    print("Message sent to " + username + "!")
    return 0

def seePrivateMessages():
    print("You have no new messages")
    return 0

