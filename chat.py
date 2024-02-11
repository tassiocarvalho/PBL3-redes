import socket
import threading
import os
import platform
import json
import uuid
import time

class ChatP2P:
    def __init__(self):
        self.usuarios = ["192.168.1.5", "192.168.1.14"]
        self.porta = 5111
        self.mensagens_recebidas = []
        self.sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recebimento.bind(('0.0.0.0', self.porta))
        self.sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.id = uuid.uuid4()
        self.ack_timeout = 5  # Tempo limite para esperar um ACK em segundos

    def clear_screen(self):
        """Função para limpar a tela de forma multiplataforma"""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    def receber_mensagens(self):
        """Função para receber mensagens"""
        while True:
            mensagem, endereco = self.sock_recebimento.recvfrom(1024)
            mensagem_decodificada = json.loads(mensagem.decode('utf-8'))
            mensagem_id = mensagem_decodificada.get('id', None)

            # Verificar se a mensagem é um ACK
            if mensagem_decodificada.get('tipo') == 'ACK' and mensagem_id:
                self.tratar_ack(mensagem_id)
            else:
                self.mensagens_recebidas.append((endereco, mensagem_decodificada['mensagem']))
                self.enviar_ack(endereco, mensagem_id)
                self.clear_screen()
                print("Mensagens Recebidas:")
                for endereco, mensagem in self.mensagens_recebidas:
                    print(f"{endereco}: {mensagem}")
                print("\nDigite a mensagem a ser enviada:")

    def tratar_ack(self, mensagem_id):
        """Função para tratar o recebimento de um ACK"""
        # Remover a mensagem da lista de mensagens enviadas pendentes
        pass  # Implementar conforme necessário

    def enviar_ack(self, endereco, mensagem_id):
        """Função para enviar um ACK"""
        ack = json.dumps({'id': str(self.id), 'tipo': 'ACK', 'mensagem_id': mensagem_id})
        self.sock_envio.sendto(ack.encode('utf-8'), endereco)

    def enviar_mensagem(self, mensagem):
        """Função para enviar uma mensagem"""
        mensagem_json = json.dumps({'id': str(self.id), 'mensagem': mensagem})
        for usuario in self.usuarios:
            try:
                self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

    def iniciar_chat(self):
        """Método para iniciar o chat"""
        thread_recebimento = threading.Thread(target=self.receber_mensagens)
        thread_recebimento.daemon = True
        thread_recebimento.start()

        while True:
            mensagem = input()
            self.enviar_mensagem(mensagem)

# Iniciar o chat
chat = ChatP2P()
chat.iniciar_chat()
