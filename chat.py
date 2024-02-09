import socket
import threading
import time

data_users = [
    #{"host": '172.16.103.1', "port": 1111, "nome": "Abraao"},
    #{"host": '172.16.103.2', "port": 2222, "nome": "Bruna"},
    #{"host": '172.16.103.3', "port": 3333, "nome": "Caio"},
    #{"host": '10.65.138.64', "port": 4444, "nome": "Daniela"},
    #{"host": '10.65.128.250', "port": 5555, "nome": "Edu"},
    #{"host": '192.168.1.200', "port": 6666, "nome": "Fernanda"},
    #{"host": '172.16.103.4', "port": 3332, "nome": "alk"},
    #{"host": '172.16.103.5', "port": 3334, "nome": "marco"},
    #{"host": '172.16.103.6', "port": 3335, "nome": "silva"},
    #{"host": '172.16.103.7', "port": 3336, "nome": "freitas"},
    #{"host": '172.16.103.8', "port": 3337, "nome": "pedro"},
    #{"host": '172.16.103.9', "port": 3338, "nome": "santos"}
    {"host": '192.168.1.14', "port": 7626, "nome": "Gabriel"},
    {"host": '192.168.1.5', "port": 7666, "nome": "pangi"}
]

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
        print("Aguardando mensagens na porta", port)
        while True:
            data, addr = s.recvfrom(buffer_size)
            received_message = data.decode()
            sender = next((user["nome"] for user in data_users if user["port"] == port), "Desconhecido")
            print(f"{sender}: {received_message}")
            time.sleep(0.5)  # Ajustado para 0.1 segundo
    except Exception as e:
        print("Erro ao receber mensagem:", e)
    finally:
        s.close()

def start_user(user):
    next_index = (data_users.index(user) + 1) % len(data_users)
    next_user = data_users[next_index]
    threading.Thread(target=receive_message, args=(user["port"],)).start()
    while True:
        message = input("Digite uma mensagem para enviar: ")
        send_message(next_user["host"], next_user["port"], message)
        time.sleep(0.1)  # Ajustado para 0.1 segundo

if __name__ == "__main__":
    for user in data_users:
        threading.Thread(target=start_user, args=(user,)).start()
