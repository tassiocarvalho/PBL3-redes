import os
import socket
import threading
import time

data_users = [
    {"host": '192.168.1.14', "port": 7626},
    {"host": '192.168.1.5', "port": 7666},
    {"host": '192.168.1.12', "port": 7662}
]

# Variáveis globais para manter a ordem das mensagens
message_queue = []  # Fila de mensagens a serem enviadas
message_lock = threading.Lock()  # Lock para garantir a sincronização na manipulação da fila

def send_message(host, port, message):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.sendto(message.encode(), (host, port))
        s.close()
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def receive_message(port, buffer_size=1024):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', port))
        print(f"Aguardando mensagens na porta {port}")
        while True:
            data, addr = s.recvfrom(buffer_size)
            received_message = data.decode()
            print(received_message)
            with message_lock:
                message_queue.append(received_message)
            time.sleep(0.5)
    except Exception as e:
        print("Erro ao receber mensagem:", e)
    finally:
        s.close()

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_chat_history():
    clear_terminal()
    with message_lock:
        for message in message_queue:
            print(message)

if __name__ == "__main__":
    for user in data_users:
        threading.Thread(target=receive_message, args=(user["port"],)).start()

    while True:
        message = input("Digite uma mensagem para enviar para o grupo: ")
        display_chat_history()
        with message_lock:
            message_queue.append(f"Você: {message}")
            for i, user in enumerate(data_users):
                next_user = data_users[(i + 1) % len(data_users)]  # Próximo usuário no anel
                send_message(next_user["host"], next_user["port"], message)
