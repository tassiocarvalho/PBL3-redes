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

# Tempo limite para esperar pela confirmação (em segundos)
timeout = 5

# Mensagem especial para solicitar a retransmissão de mensagens perdidas
MENSAGEM_RETRANSMISSAO = "__RETRANSMITIR__"

# Função para limpar a tela de forma multiplataforma
def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# Lista para armazenar as mensagens recebidas
mensagens_recebidas = []

# Dicionário para manter o controle das mensagens enviadas e seus status de confirmação
mensagens_enviadas = {}

# Função para receber mensagens
def receber_mensagens():
    # Socket UDP para recebimento de mensagens
    sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_recebimento.bind(('0.0.0.0', porta))

    while True:
        mensagem, endereco = sock_recebimento.recvfrom(1024)
        # Decodificar a mensagem JSON
        mensagem_decodificada = json.loads(mensagem.decode('utf-8'))
        
        if mensagem_decodificada['mensagem'] == MENSAGEM_RETRANSMISSAO:
            # Mensagem de solicitação de retransmissão, reenviar mensagens não confirmadas
            reenviar_mensagens_nao_confirmadas()
        else:
            # Adicionar mensagem recebida à lista
            mensagens_recebidas.append((endereco, mensagem_decodificada['mensagem']))
            # Limpar a tela e exibir as mensagens recebidas
            clear_screen()
            print("Mensagens Recebidas:")
            for endereco, mensagem in mensagens_recebidas:
                print(f"{endereco}: {mensagem}")
            print("\nDigite a mensagem a ser enviada:")
        
        # Verificar se a mensagem recebida corresponde a uma mensagem enviada anteriormente e não confirmada
        for mensagem_enviada, tempo_envio in mensagens_enviadas.items():
            if mensagem_enviada == mensagem_decodificada['mensagem'] and time.time() - tempo_envio > timeout:
                # A mensagem não foi confirmada e o tempo limite foi atingido, reenviar
                enviar_mensagem(mensagem_enviada)

# Função para enviar uma mensagem
def enviar_mensagem(mensagem):
    # Socket UDP para envio de mensagens
    sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Codificar a mensagem para JSON
    mensagem_json = json.dumps({'mensagem': mensagem})

    # Enviar a mensagem para cada usuário na lista de usuários
    for usuario in usuarios:
        try:
            sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, porta))
            # Registrar o tempo de envio da mensagem
            mensagens_enviadas[mensagem] = time.time()
        except Exception as e:
            print(f"Erro ao enviar mensagem para {usuario}: {e}")

# Função para reenviar mensagens não confirmadas
def reenviar_mensagens_nao_confirmadas():
    for mensagem, tempo_envio in mensagens_enviadas.items():
        if time.time() - tempo_envio > timeout:
            # Mensagem não foi confirmada e o tempo limite foi atingido, reenviar
            enviar_mensagem(mensagem)

# Inicializar a thread para receber mensagens
thread_recebimento = threading.Thread(target=receber_mensagens)
thread_recebimento.daemon = True
thread_recebimento.start()

# Manter o programa em execução
while True:
    mensagem = input("Digite a mensagem a ser enviada: ")
    enviar_mensagem(mensagem)
