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

# Lista para armazenar as mensagens recebidas
mensagens_recebidas = []

# Lista para armazenar as mensagens enviadas e não confirmadas
mensagens_enviadas = []

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
        mensagem = input("Digite a mensagem a ser enviada: ")
        # Gerar um identificador único para a mensagem
        id_mensagem = time.time()
        # Codificar a mensagem para JSON
        mensagem_json = json.dumps({'id': id_mensagem, 'mensagem': mensagem})
        # Adicionar a mensagem à lista de mensagens enviadas
        mensagens_enviadas.append((mensagem_json, time.time()))
        # Enviar a mensagem para o próximo usuário na lista de usuários
        for usuario in usuarios:
            try:
                sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, porta))
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")
        
        # Aguardar um curto período antes de verificar os ACKs
        time.sleep(1)
        
        # Verificar ACKs para mensagens enviadas
        for index, (mensagem, tempo_envio) in enumerate(mensagens_enviadas):
            if time.time() - tempo_envio >= 5:  # Se passaram 5 segundos desde o envio
                print(f"Reenviando mensagem: {mensagem}")
                for usuario in usuarios:
                    try:
                        sock_envio.sendto(mensagem.encode('utf-8'), (usuario, porta))
                    except Exception as e:
                        print(f"Erro ao reenviar mensagem para {usuario}: {e}")
                # Atualizar o tempo de envio da mensagem
                mensagens_enviadas[index] = (mensagem, time.time())

# Inicializar a thread para enviar mensagens
thread_envio = threading.Thread(target=enviar_mensagens)
thread_envio.daemon = True
thread_envio.start()

# Manter o programa em execução
while True:
    pass
