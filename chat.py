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
        # Codificar a mensagem para JSON
        mensagem_json = json.dumps({'mensagem': mensagem})
        # Enviar a mensagem para cada usuário na lista de usuários
        for usuario in usuarios:
            try:
                sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, porta))
                # Registrar a mensagem enviada e o tempo atual
                mensagens_enviadas[mensagem] = time.time()
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

        # Aguardar confirmações de recebimento
        esperar_confirmacoes()

# Função para aguardar confirmações de recebimento
def esperar_confirmacoes():
    inicio = time.time()
    while True:
        # Verificar se algum tempo limite foi atingido
        if time.time() - inicio > timeout:
            # Reenviar mensagens não confirmadas
            reenviar_mensagens_nao_confirmadas()
            break

        # Verificar se todas as mensagens enviadas foram confirmadas
        todas_confirmadas = all(mensagem in mensagens_recebidas for mensagem in mensagens_enviadas.keys())
        if todas_confirmadas:
            break

# Função para reenviar mensagens não confirmadas
def reenviar_mensagens_nao_confirmadas():
    for mensagem, tempo_envio in mensagens_enviadas.items():
        # Verificar se a mensagem não foi confirmada e o tempo limite foi atingido
        if mensagem not in [mensagem for _, mensagem in mensagens_recebidas] and time.time() - tempo_envio > timeout:
            # Reenviar a mensagem para cada usuário na lista de usuários
            mensagem_json = json.dumps({'mensagem': mensagem})
            for usuario in usuarios:
                try:
                    sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, porta))
                    # Atualizar o tempo de envio da mensagem
                    mensagens_enviadas[mensagem] = time.time()
                except Exception as e:
                    print(f"Erro ao reenviar mensagem para {usuario}: {e}")

# Inicializar a thread para enviar mensagens
thread_envio = threading.Thread(target=enviar_mensagens)
thread_envio.daemon = True
thread_envio.start()

# Manter o programa em execução
while True:
    pass
