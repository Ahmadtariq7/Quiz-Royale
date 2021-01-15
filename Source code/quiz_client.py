import socket
from fl_networking_tools import get_binary, send_binary

'''
COMMANDS
JOIN - client requesting to join quiz
QUES - send the next question
ANSW - sending answer
STAT - Status of Quiz

Responses:
1 - Join request confirmed
2 - Join request denied
3 - Question available
4 - Question
5 - Answer correct
6 - Answer incorrect
7 - Quiz Over
'''

# A flag used to control the quiz loop.
playing = True

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

team_name = input("What is your team name?")

client_socket.connect(("127.0.0.1", 8081))

# Sending a command to the server.
send_binary(client_socket, ["JOIN", team_name])

while playing:
    # The get_binary function returns a list of messages - loop over them
    for response in get_binary(client_socket):
        if response[0] == 1: 
            print("Welcome to the quiz team - " + str(team_name))
            send_binary(client_socket, ["STAT", 1])
        elif response[0] == 2:
            print("Access Denied")
            playing =False
        elif response[0] == 3:
            print(response[1])
            send_binary(client_socket, ["QUES", ""])
        elif response[0] == 4:
            print(response[1])
            answer = input(">")
            send_binary(client_socket, ["ANSW", answer])
        elif response[0] == 5:
            print("Correct well done")
            print(":your score is... " + str(response[1]))
            send_binary(client_socket,["STAT", ""])
        elif response[0] == 6:
            print("Incorrect sorry")
            send_binary(client_socket, ["STAT", ""])
        elif response[0] == 7:
            send_binary(client_socket, ["QUES", ""])
            print("Next Question")
        elif response[0] == 8:
            print("Quiz Finished!")
            playing = False

