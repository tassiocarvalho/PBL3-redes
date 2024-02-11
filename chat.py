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

# Função para limpar a tela de forma multiplataforma
def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# Lista para armazenar as mensagens enviadas e seus identificadores
mensagens_enviadas = []

# Lista para armazenar as mensagens recebidas
mensagens_recebidas = []

# Dicionário para armazenar os ACKs recebidos
acks_recebidos = {}

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
        if mensagem_decodificada['id'] not in [msg[0] for msg in mensagens_recebidas]:
            mensagens_recebidas.append((mensagem_decodificada['id'], endereco, mensagem_decodificada['mensagem']))
            # Enviar um ACK de volta para o remetente
            sock_recebimento.sendto(json.dumps({'ack': mensagem_decodificada['id']}).encode('utf-8'), endereco)
            # Limpar a tela e exibir as mensagens recebidas
            clear_screen()
            print("Mensagens Recebidas:")
            for id_mensagem, endereco, mensagem in mensagens_recebidas:
                print(f"{id_mensagem} - {endereco}: {mensagem}")
            print("\nDigite a mensagem a ser enviada:")

# Inicializar a thread para receber mensagens
thread_recebimento = threading.Thread(target=receber_mensagens)
thread_recebimento.daemon = True
thread_recebimento.start()

# Função para enviar mensagens
def enviar_mensagens():
    # Socket UDP para envio de mensagens
    sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        mensagem = input()
        # Gerar um ID único para a mensagem
        id_mensagem = str(time.time())
        # Codificar a mensagem para JSON
        mensagem_json = json.dumps({'id': id_mensagem, 'mensagem': mensagem})
        # Adicionar a mensagem enviada à lista de mensagens enviadas
        mensagens_enviadas.append((id_mensagem, mensagem))
        # Enviar a mensagem para o próximo usuário na lista de usuários
        for usuario in usuarios:
            try:
                sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, porta))
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")
        # Aguardar o ACK para a mensagem enviada
        aguardar_ack(id_mensagem)

# Função para aguardar o ACK para uma mensagem enviada
def aguardar_ack(id_mensagem):
    global acks_recebidos
    # Definir um timeout para aguardar o ACK
    timeout = 5
    tempo_inicio = time.time()
    while time.time() - tempo_inicio < timeout:
        if id_mensagem in acks_recebidos:
            del acks_recebidos[id_mensagem]
            break

# Inicializar a thread para enviar mensagens
thread_envio = threading.Thread(target=enviar_mensagens)
thread_envio.daemon = True
thread_envio.start()

# Função para receber ACKs
def receber_acks():
    global acks_recebidos
    # Socket UDP para recebimento de ACKs
    sock_acks = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_acks.bind(('0.0.0.0', porta + 1))

    while True:
        ack, endereco = sock_acks.recvfrom(1024)
        ack_decodificado = json.loads(ack.decode('utf-8'))
        # Adicionar o ACK recebido ao dicionário
        acks_recebidos[ack_decodificado['ack']] = True

# Inicializar a thread para receber ACKs
thread_acks = threading.Thread(target=receber_acks)
thread_acks.daemon = True
thread_acks.start()

# Manter o programa em execução
while True:
    pass
