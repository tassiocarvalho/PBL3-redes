import socket
import threading
import os
import platform
import json

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

# Função para receber mensagens
def receber_mensagens():
    # Socket UDP para recebimento de mensagens
    sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_recebimento.bind(('0.0.0.0', porta))

    while True:
        mensagem, endereco = sock_recebimento.recvfrom(1024)
        mensagem_str = mensagem.decode('utf-8')
        # Verificar se a mensagem termina com '/'
        if mensagem_str.endswith('/'):
            # Contar o número de ocorrências da marca '/'
            num_barras = mensagem_str.count('/')
            # Adicionar mensagem recebida à lista
            mensagens_recebidas.append((endereco, mensagem_str))
            # Limpar a tela e exibir as mensagens recebidas
            clear_screen()
            print("Mensagens Recebidas:")
            for endereco, mensagem in mensagens_recebidas:
                # Exibir uma marca extra para cada ocorrência adicional de '/'
                marca_extra = '/' * (num_barras - 1)
                print(f"{endereco}: {mensagem}{marca_extra}")
            print("\nDigite a mensagem a ser enviada:")
        else:
            print("Erro: Mensagem recebida inválida:", mensagem_str)



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
        # Enviar a mensagem para o próximo usuário na lista de usuários
        for usuario in usuarios:
            try:
                sock_envio.sendto(mensagem_json.encode('utf-8') + b'/', (usuario, porta))
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

# Inicializar a thread para enviar mensagens
thread_envio = threading.Thread(target=enviar_mensagens)
thread_envio.daemon = True
thread_envio.start()

# Manter o programa em execução
while True:
    pass
