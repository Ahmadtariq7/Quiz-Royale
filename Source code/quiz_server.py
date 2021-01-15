import socketserver
from threading import Event
from random import choice
from collections import namedtuple
from fl_networking_tools import get_binary, send_binary

'''
Commands:
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

players = []
ready_to_start = Event()

answered = 0
wait_for_answers = Event()

# Dictionary of scores
scores = {}

# >> Questions
Question = namedtuple('Question', ['q', 'answer'])

quiz_questions = [
    Question("Expand the acronym ALU", "Arithmetic Logic Unit"),
    Question("What does RAM Stand for?", "Random Access Memory"),
    Question("Most popular search engine", "Google"),
    Question("Who is the owner of Tesla?", "Elon Musk"),
    Question("What does CS Stand for?", "Computer Science")

]


current_question = None

# MAX_PLAYERS = 1
# while MAX_PLAYERS:
#     try:
MAX_PLAYERS = input("How many players would you like?")
MAX_PLAYERS = int(MAX_PLAYERS)
print("Waiting for Clients to Join....")
    # except:
    #     print("Try again please.")

answered = 0


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


# The socketserver module uses 'Handlers' to interact with connections. When a client connects a version of this class is made to handle it.
class QuizGame(socketserver.BaseRequestHandler):
    # The handle method is what actually handles the connection
    def handle(self):
        global players, answered, current_question, scores
        playing = True
        while playing:
            for command in get_binary(self.request):
                if command[0] == "JOIN":
                    team_name = command[1]
                    scores[team_name] = 0
                    players.append(team_name)
                    print(players[0])
                    if len(players) < MAX_PLAYERS:
                        send_binary(self.request, [1, ""])
                    elif len(players) > MAX_PLAYERS:
                        send_binary(self.request, [2, ""])
                    else:
                        send_binary(self.request, [1, ""])
                        ready_to_start.set()
                    ready_to_start.wait()
                elif command[0] == "STAT":
                    if ready_to_start.isSet() and not wait_for_answers.isSet():
                        send_binary(self.request, [3, "Quiz is starting!"])
                    elif ready_to_start.isSet() and wait_for_answers.isSet():
                        send_binary(self.request, [3, "Quiz Continuing!"])
                elif command[0] == "QUES":
                    if current_question is None:
                        current_question = choice(quiz_questions)
                        wait_for_answers.clear()
                    send_binary(self.request, [4, current_question.q])
                elif command[0] == "ANSW":
                    if command[1].lower() == current_question.answer.lower():
                        scores[team_name] += 1
                        response = 5
                    else:
                        response = 6
                    send_binary(self.request, [response, scores[team_name]])
                    answered += 1
                    if answered == len(players):
                        quiz_questions.remove(current_question)
                        current_question = None
                        wait_for_answers.set()
                    wait_for_answers.wait()

        self.request.send(bytes([8]))


# Open the quiz server and bind it to a port - creating a socket
quiz_server = socketserver.TCPServer(('0.0.0.0', 8081), QuizGame)
quiz_server.serve_forever()
