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

# Timeout para aguardar a confirmação de recebimento (em segundos)
timeout_ack = 5

# Função para limpar a tela de forma multiplataforma
def clear_screen():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')

# Estrutura de dados para rastrear mensagens enviadas e seus status de confirmação
mensagens_enviadas = {}

# Lista para armazenar as mensagens recebidas
mensagens_recebidas = []

# Função para receber mensagens
def receber_mensagens(sock_recebimento, sock_envio):
    while True:
        mensagem, endereco = sock_recebimento.recvfrom(1024)
        # Decodificar a mensagem JSON
        mensagem_decodificada = json.loads(mensagem.decode('utf-8'))
        # Adicionar mensagem recebida à lista
        mensagem_id = mensagem_decodificada['id']
        mensagem_texto = mensagem_decodificada['mensagem']
        mensagens_recebidas.append((endereco, mensagem_texto))
        # Enviar uma confirmação (ACK) de recebimento para o remetente
        enviar_ack(endereco, mensagem_id, sock_envio)

# Função para enviar uma confirmação (ACK) de recebimento
def enviar_ack(endereco, mensagem_id, sock_envio):
    mensagem_ack = json.dumps({'id': mensagem_id, 'ack': True})
    sock_envio.sendto(mensagem_ack.encode('utf-8'), endereco)

# Função para enviar mensagens
def enviar_mensagens(sock_envio):
    while True:
        mensagem = input()
        # Gerar um identificador único para a mensagem
        mensagem_id = time.time()  # Usando o timestamp como identificador único
        # Codificar a mensagem para JSON
        mensagem_json = json.dumps({'id': mensagem_id, 'mensagem': mensagem})
        # Enviar a mensagem para o próximo usuário na lista de usuários
        for usuario in usuarios:
            try:
                sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, porta))
                # Adicionar a mensagem à lista de mensagens enviadas
                mensagens_enviadas[mensagem_id] = {'mensagem': mensagem, 'enviada_em': time.time(), 'confirmada': False}
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

# Função para verificar e reenviar mensagens não confirmadas
def verificar_reenvio(sock_envio):
    while True:
        # Verificar cada mensagem enviada
        for mensagem_id, mensagem_info in mensagens_enviadas.items():
            if not mensagem_info['confirmada']:
                # Se a mensagem não foi confirmada dentro do tempo limite, reenviar
                if time.time() - mensagem_info['enviada_em'] > timeout_ack:
                    mensagem_json = json.dumps({'id': mensagem_id, 'mensagem': mensagem_info['mensagem']})
                    for usuario in usuarios:
                        sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, porta))
        # Aguardar um intervalo antes de verificar novamente
        time.sleep(1)

def main():
    # Socket UDP para recebimento de mensagens
    sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_recebimento.bind(('0.0.0.0', porta))

    # Socket UDP para envio de mensagens
    sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Inicializar as threads para receber mensagens, enviar mensagens e verificar reenvio
    thread_recebimento = threading.Thread(target=receber_mensagens, args=(sock_recebimento, sock_envio))
    thread_recebimento.daemon = True
    thread_recebimento.start()

    thread_envio = threading.Thread(target=enviar_mensagens, args=(sock_envio,))
    thread_envio.daemon = True
    thread_envio.start()

    thread_verificar_reenvio = threading.Thread(target=verificar_reenvio, args=(sock_envio,))
    thread_verificar_reenvio.daemon = True
    thread_verificar_reenvio.start()

    # Manter o programa em execução
    while True:
        pass

if __name__ == "__main__":
    main()
