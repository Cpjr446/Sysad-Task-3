import socket

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "Disconnected"
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    response = client.recv(2048).decode(FORMAT)
    return response

def register(username, password):
    return send(f"REGISTER {username} {password}")

def login(username, password):
    response = send(f"LOGIN {username} {password}")
    if "Login successful" in response:
        return response.split()[-1]  # Assuming user_id is the last word in the response
    else:
        print(response)
        return None

def add_question(user_id, question_id, question, answer):
    return send(f"ADD_QUESTION {user_id} {question_id} '{question}' '{answer}'")

def answer_question(user_id, question_id, answer):
    return send(f"ANSWER {user_id} {question_id} '{answer}'")

def view_leaderboard():
    return send("LEADERBOARD")

def main():
    while True:
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            print(register(username, password))
        elif choice == '2':
            username = input("Enter username: ")
            password = input("Enter password: ")
            user_id = login(username, password)
            if user_id:
                while True:
                    print("1. Add question")
                    print("2. Answer question")
                    print("3. View leaderboard")
                    print("4. Logout")
                    choice = input("Enter your choice: ")

                    if choice == '1':
                        question_id = input("Enter the question ID: ")  
                        question = input("Enter the question: ")
                        answer = input("Enter the answer: ")
                        print(add_question(user_id, question_id, question, answer))
                    elif choice == '2':
                        question_id = input("Enter question ID: ")
                        answer = input("Enter your answer: ")
                        print(answer_question(user_id, question_id, answer))
                    elif choice == '3':
                        print(view_leaderboard())
                    elif choice == '4':
                        print("Logged out")
                        break
                    else:
                        print("Invalid choice")
            else:
                print("Login failed")
        elif choice == '3':
            send(DISCONNECT_MESSAGE)
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
