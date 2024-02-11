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

# Lista para armazenar as mensagens pendentes de entrega
mensagens_pendentes = []

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
        mensagens_recebidas.append((endereco, mensagem_decodificada['mensagem']))
        # Limpar a tela e exibir as mensagens recebidas
        clear_screen()
        print("Mensagens Recebidas:")
        for endereco, mensagem in mensagens_recebidas:
            print(f"{endereco}: {mensagem}")
        print("\nDigite a mensagem a ser enviada:")
        
        # Tentar reenviar mensagens pendentes
        reenviar_mensagens_pendentes()

# Função para enviar mensagens
def enviar_mensagens():
    # Socket UDP para envio de mensagens
    sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    while True:
        mensagem = input()
        # Codificar a mensagem para JSON
        mensagem_json = json.dumps({'mensagem': mensagem})
        # Enviar a mensagem para cada usuário na lista de usuários
        for usuario in usuarios:
            try:
                sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, porta))
                # Registrar a mensagem enviada e o tempo atual
                mensagens_enviadas[mensagem] = time.time()
                # Adicionar a mensagem à lista de mensagens pendentes
                mensagens_pendentes.append(mensagem)
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

        # Aguardar confirmações de recebimento
        time.sleep(1)  # Adicionar um pequeno atraso para evitar reenvios excessivos

# Função para reenviar mensagens pendentes
def reenviar_mensagens_pendentes():
    for mensagem in mensagens_pendentes:
        if mensagem not in [mensagem for _, mensagem in mensagens_recebidas]:
            # Mensagem não foi confirmada, reenviar para cada usuário
            mensagem_json = json.dumps({'mensagem': mensagem})
            for usuario in usuarios:
                try:
                    sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, porta))
                except Exception as e:
                    print(f"Erro ao reenviar mensagem para {usuario}: {e}")

# Inicializar a thread para receber mensagens
thread_recebimento = threading.Thread(target=receber_mensagens)
thread_recebimento.daemon = True
thread_recebimento.start()

# Inicializar a thread para enviar mensagens
thread_envio = threading.Thread(target=enviar_mensagens)
thread_envio.daemon = True
thread_envio.start()

# Manter o programa em execução
while True:
    pass
