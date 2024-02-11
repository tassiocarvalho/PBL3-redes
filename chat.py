import socket
import threading
import os
import platform
import json
import time

# Lista de IPs dos usuários
usuarios = ["192.168.1.5", "192.168.1.14"]

# Porta para comunicação
porta = 5111

# Dicionário para armazenar o status de entrega de cada mensagem
status_entrega = {}

# Função para limpar a tela de forma multiplataforma
def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# Função para receber mensagens
def receber_mensagens():
    # Socket UDP para recebimento de mensagens
    sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_recebimento.bind(('0.0.0.0', porta))

    while True:
        mensagem, endereco = sock_recebimento.recvfrom(1024)
        # Decodificar a mensagem JSON
        mensagem_decodificada = json.loads(mensagem.decode('utf-8'))
        # Adicionar mensagem recebida à lista
        mensagem_recebida = mensagem_decodificada['mensagem']
        mensagens_recebidas.append((endereco, mensagem_recebida))
        # Limpar a tela e exibir as mensagens recebidas
        clear_screen()
        print("Mensagens Recebidas:")
        for endereco, mensagem in mensagens_recebidas:
            print(f"{endereco}: {mensagem}")
        print("\nDigite a mensagem a ser enviada:")

# Função para enviar mensagens
def enviar_mensagem(mensagem, destinatario):
    # Socket UDP para envio de mensagens
    sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Codificar a mensagem para JSON
    mensagem_json = json.dumps({'mensagem': mensagem})

    try:
        # Enviar a mensagem para o destinatário
        sock_envio.sendto(mensagem_json.encode('utf-8'), (destinatario, porta))
        # Registrar o status de entrega da mensagem como pendente
        status_entrega[mensagem] = False
        # Aguardar a confirmação de entrega (ACK) por um tempo limitado
        sock_envio.settimeout(5)  # 5 segundos de timeout
        ack, _ = sock_envio.recvfrom(1024)
        print(f"ACK recebido de {destinatario} para mensagem: {mensagem}")
        # Registrar o status de entrega da mensagem como entregue
        status_entrega[mensagem] = True
    except socket.timeout:
        print(f"Timeout ao aguardar ACK de {destinatario} para mensagem: {mensagem}. Reenviando mensagem.")
        # Reenviar a mensagem em caso de timeout
        enviar_mensagem(mensagem, destinatario)
    except Exception as e:
        print(f"Erro ao enviar mensagem para {destinatario}: {e}")

# Função para enviar mensagens com feedback de entrega
def enviar_mensagens():
    while True:
        mensagem = input("Digite a mensagem a ser enviada: ")
        for usuario in usuarios:
            enviar_mensagem(mensagem, usuario)
            # Verificar se a mensagem foi entregue com sucesso
            if status_entrega.get(mensagem, False):
                print(f"Mensagem '{mensagem}' enviada com sucesso para {usuario}.")
            else:
                print(f"Erro ao enviar mensagem '{mensagem}' para {usuario}.")

# Inicializar a thread para receber mensagens
thread_recebimento = threading.Thread(target=receber_mensagens)
thread_recebimento.daemon = True
thread_recebimento.start()

# Inicializar a thread para enviar mensagens
thread_envio = threading.Thread(target=enviar_mensagens)
thread_envio.daemon = True
thread_envio.start()

# Lista para armazenar as mensagens recebidas
mensagens_recebidas = []

# Manter o programa em execução
while True:
    pass
