import os
import socket
import threading
import time
import queue

data_users = [
    {"host": '192.168.1.14', "port": 7626},
    {"host": '192.168.1.5', "port": 7666},
    {"host": '192.168.1.12', "port": 7662}
]

# Lista para armazenar as mensagens recebidas
chat_history = []

# Número de mensagens no histórico no momento da última atualização
last_history_length = 0

# Fila para manter as mensagens a serem enviadas
message_queue = queue.Queue()

def send_message(host, port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(message.encode(), (host, port))
        s.close()
    except Exception as e:
        print(f"Erro ao enviar mensagem para {host}:{port}: {e}")

def send_message_to_all_except_self(current_host, current_port, message):
    for user in data_users:
        if user["host"] != current_host or user["port"] != current_port:
            send_message(user["host"], user["port"], message)

def receive_message(port, buffer_size=1024):
    global last_history_length
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', port))
        while True:
            data, addr = s.recvfrom(buffer_size)
            received_message = data.decode()
            print(received_message)
            chat_history.append(received_message)  # Adiciona a mensagem recebida ao histórico de chat
            last_history_length = len(chat_history)  # Atualiza o número de mensagens no histórico
    except Exception as e:
        print("Erro ao receber mensagem:", e)
    finally:
        s.close()

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_chat_history():
    clear_terminal()
    for message in chat_history:
        print(message)

def update_chat_history():
    while True:
        time.sleep(0.1)  # Atualiza a cada 0.1 segundos
        display_chat_history()

if __name__ == "__main__":
    for user in data_users:
        threading.Thread(target=receive_message, args=(user["port"],)).start()

    threading.Thread(target=update_chat_history).start()

    while True:
        message = input("Digite uma mensagem para enviar para o grupo: ")
        message_queue.put(f"Você: {message}")
        threading.Thread(target=send_message_to_all_except_self, args=(socket.gethostbyname(socket.gethostname()), data_users[0]["port"], f"Você: {message}")).start()
