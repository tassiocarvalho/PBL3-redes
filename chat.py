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

# Tempo limite para aguardar uma confirmação de recebimento (em segundos)
tempo_limite_ack = 5

# Função para limpar a tela de forma multiplataforma
def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# Lista para armazenar as mensagens enviadas
mensagens_enviadas = {}

# Socket UDP para envio de mensagens
sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Função para receber mensagens
def receber_mensagens():
    # Socket UDP para recebimento de mensagens
    sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_recebimento.bind(('0.0.0.0', porta))

    while True:
        mensagem, endereco = sock_recebimento.recvfrom(1024)
        # Decodificar a mensagem JSON
        mensagem_decodificada = json.loads(mensagem.decode('utf-8'))
        if mensagem_decodificada['tipo'] == 'mensagem':
            # Adicionar mensagem recebida à lista
            mensagem_recebida = mensagem_decodificada['mensagem']
            print(f"Mensagem recebida de {endereco}: {mensagem_recebida}")
            # Enviar ACK de volta ao remetente
            ack = {'tipo': 'ack', 'id': mensagem_decodificada['id']}
            sock_envio.sendto(json.dumps(ack).encode('utf-8'), endereco)
        elif mensagem_decodificada['tipo'] == 'ack':
            # Remover mensagem da lista de mensagens enviadas quando o ACK é recebido
            if mensagem_decodificada['id'] in mensagens_enviadas:
                del mensagens_enviadas[mensagem_decodificada['id']]

# Inicializar a thread para receber mensagens
thread_recebimento = threading.Thread(target=receber_mensagens)
thread_recebimento.daemon = True
thread_recebimento.start()

# Função para enviar mensagens
def enviar_mensagens():
    while True:
        mensagem = input("Digite a mensagem a ser enviada: ")
        mensagem_id = time.time()
        mensagem_json = {'tipo': 'mensagem', 'mensagem': mensagem, 'id': mensagem_id}
        # Enviar a mensagem para todos os usuários na lista de usuários
        for usuario in usuarios:
            try:
                sock_envio.sendto(json.dumps(mensagem_json).encode('utf-8'), (usuario, porta))
                # Adicionar mensagem à lista de mensagens enviadas
                mensagens_enviadas[mensagem_id] = mensagem_json
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

# Inicializar a thread para enviar mensagens
thread_envio = threading.Thread(target=enviar_mensagens)
thread_envio.daemon = True
thread_envio.start()

# Função para verificar mensagens não confirmadas e reenviá-las se necessário
def verificar_ack():
    while True:
        # Verificar mensagens enviadas não confirmadas
        for mensagem_id, mensagem_info in list(mensagens_enviadas.items()):
            if time.time() - mensagem_info['id'] > tempo_limite_ack:
                # Reenviar mensagem se o ACK não for recebido dentro do tempo limite
                print(f"Mensagem não confirmada: {mensagem_info['mensagem']}. Reenviando...")
                for usuario in usuarios:
                    try:
                        sock_envio.sendto(json.dumps(mensagem_info).encode('utf-8'), (usuario, porta))
                    except Exception as e:
                        print(f"Erro ao reenviar mensagem para {usuario}: {e}")
                # Remover mensagem da lista de mensagens enviadas para evitar reenvios duplicados
                del mensagens_enviadas[mensagem_id]
        time.sleep(1)  # Aguardar 1 segundo antes de verificar novamente

# Inicializar a thread para verificar mensagens não confirmadas
thread_verificar_ack = threading.Thread(target=verificar_ack)
thread_verificar_ack.daemon = True
thread_verificar_ack.start()

# Manter o programa em execução
while True:
    pass
