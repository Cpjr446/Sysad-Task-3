import socket
import threading
import mysql.connector
from mysql.connector import errorcode
from hashlib import sha256
import os

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "Disconnected"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

# Database connection details from environment variables
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_USER = os.getenv('DB_USER', 'mysql')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'Del24Sysad$$')
DB_NAME = os.getenv('DB_NAME', 'quiz')

# Create a lock object to ensure thread safety for database operations
db_lock = threading.Lock()

# Initialize database
def init_db():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.database = DB_NAME
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_by INT,
            FOREIGN KEY (created_by) REFERENCES users (id)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            user_id INT,
            score INT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your username or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

# Connect to the database
def get_db_connection():
    conn = mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    return conn

def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
        msg_length = conn.recv(HEADER).decode(FORMAT)
        if msg_length:
            msg_length = int(msg_length)
            msg = conn.recv(msg_length).decode(FORMAT)
            print(f"[{addr}] {msg}")
            response = handle_message(msg)
            conn.send(response.encode(FORMAT))
            if msg == DISCONNECT_MESSAGE:
                connected = False

    conn.close()

def handle_message(msg):
    parts = msg.split(" ", 1)
    command = parts[0]
    if command == "REGISTER":
        username, password = parts[1].split(" ")
        return register_user(username, password)
    elif command == "LOGIN":
        username, password = parts[1].split(" ")
        return login_user(username, password)
    elif command == "ADD_QUESTION":
        user_id, question_id, question_answer = parts[1].split(" ", 2)
        question, answer = question_answer.split(" '", 1)
        answer = answer[:-1] 
        return add_question(user_id, question_id, question.strip("'"), answer.strip("'"))
    elif command == "ANSWER":
        user_id, question_id, answer = parts[1].split(" ", 2)
        return answer_question(user_id, question_id, answer.strip("'"))
    elif command == "LEADERBOARD":
        return get_leaderboard()
    else:
        return "Invalid command"

def register_user(username, password):
    hashed_password = sha256(password.encode()).hexdigest()
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (%s, %s)', (username, hashed_password))
        conn.commit()
        cursor.close()
        conn.close()
    return "User registered successfully"

def login_user(username, password):
    hashed_password = sha256(password.encode()).hexdigest()
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = %s AND password = %s', (username, hashed_password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
    if user:
        return f"Login successful {user[0]}"
    else:
        return "Invalid username or password"

def add_question(user_id, question_id, question, answer):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO questions (id, question, answer, created_by) VALUES (%s, %s, %s, %s)', (question_id, question, answer, user_id))
        conn.commit()
        cursor.close()
        conn.close()
    return "Question added successfully"

def answer_question(user_id, question_id, user_answer):
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT answer, created_by FROM questions WHERE id = %s', (question_id,))
        result = cursor.fetchone()
        if result:
            correct_answer, creator_id = result
            if user_id == creator_id:
                response = "You cannot answer your own question"
            elif correct_answer.lower().strip() == user_answer.lower().strip():
                cursor.execute('INSERT INTO leaderboard (user_id, score) VALUES (%s, 1) ON DUPLICATE KEY UPDATE score = score + 1', (user_id,))
                conn.commit()
                response = "Correct answer!"
            else:
                response = "Incorrect answer"
        else:
            response = "Question not found"
        cursor.close()
        conn.close()
    return response

def get_leaderboard():
    with db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT u.username, SUM(l.score) FROM leaderboard l JOIN users u ON l.user_id = u.id GROUP BY u.username ORDER BY SUM(l.score) DESC')
        leaderboard = cursor.fetchall()
        cursor.close()
        conn.close()
    return "\n".join([f"{username}: {score}" for username, score in leaderboard])


def start():
    server.listen()
    print(f"[LISTENING] Server is listening on {SERVER}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] Server is starting")
init_db()
start()
