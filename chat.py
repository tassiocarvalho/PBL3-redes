import socket
import threading
import time

data_users = [
    {"host": '192.168.1.14', "port": 7626, "nome": "Gabriel"},
    {"host": '192.168.1.5', "port": 7666, "nome": "pangi"}
]

def send_message(host, port, message, sender_name):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for user in data_users:
            if (user["host"], user["port"]) != (host, port):  # Não enviar de volta para o próprio remetente
                message_with_sender = f"{sender_name}: {message}"
                s.sendto(message_with_sender.encode(), (user["host"], user["port"]))
        s.close()
    except Exception as e:
        print("Erro ao enviar mensagem:", e)

def receive_message(port, buffer_size=1024):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', port))
        print("Aguardando mensagens na porta", port)
        while True:
            data, addr = s.recvfrom(buffer_size)
            received_message = data.decode()
            sender = next((user["nome"] for user in data_users if user["port"] == port), "Desconhecido")
            if not received_message.startswith(sender):  # Evita exibir mensagens enviadas pelo próprio remetente
                print(f"{sender}: {received_message}")
            time.sleep(0.5)  # Ajustado para 0.1 segundo
    except Exception as e:
        print("Erro ao receber mensagem:", e)
    finally:
        s.close()

if __name__ == "__main__":
    for user in data_users:
        threading.Thread(target=receive_message, args=(user["port"],)).start()

    while True:
        message = input("Digite uma mensagem para enviar para o grupo: ")
        for user in data_users:
            send_message(user["host"], user["port"], message, user["nome"])
