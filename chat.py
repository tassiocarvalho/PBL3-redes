import socket
import threading

# Lista de IPs dos usuários
usuarios = ["192.168.1.5", "192.168.1.6", "192.168.1.14", "192.168.1.7"]

# Porta para comunicação
porta = 5111

# Função para receber mensagens
def receber_mensagens():
    # Socket UDP para recebimento de mensagens
    sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_recebimento.bind(('0.0.0.0', porta))

    while True:
        mensagem, endereco = sock_recebimento.recvfrom(1024)
        print(f"Mensagem recebida de {endereco}: {mensagem.decode('utf-8')}")

# Inicializar a thread para receber mensagens
thread_recebimento = threading.Thread(target=receber_mensagens)
thread_recebimento.daemon = True
thread_recebimento.start()

# Função para enviar mensagens
def enviar_mensagens():
    # Socket UDP para envio de mensagens
    sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        mensagem = input("Digite a mensagem a ser enviada: ")
        # Enviar a mensagem para o próximo usuário na topologia de anel
        for usuario in usuarios:
            try:
                sock_envio.sendto(mensagem.encode('utf-8'), (usuario, porta))
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

# Inicializar a thread para enviar mensagens
thread_envio = threading.Thread(target=enviar_mensagens)
thread_envio.daemon = True
thread_envio.start()

# Manter o programa em execução
while True:
    pass
