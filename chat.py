import socket
import threading
import os
import platform
import json
import uuid
import time

class MensagemStorage:
    def __init__(self):
        self.historico_mensagens = {}

    def adicionar_mensagem(self, usuario, mensagem):
        """Adiciona uma mensagem ao histórico do usuário"""
        if usuario in self.historico_mensagens:
            self.historico_mensagens[usuario].append(mensagem)
        else:
            self.historico_mensagens[usuario] = [mensagem]

    def obter_historico_mensagens(self, usuario):
        """Retorna o histórico de mensagens de um usuário"""
        return self.historico_mensagens.get(usuario, [])

class ChatP2P:
    def __init__(self):
        self.usuarios = ["192.168.1.24", "192.168.1.21"]
        self.porta = 5111
        self.mensagens_recebidas = []
        self.sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recebimento.bind(('0.0.0.0', self.porta))
        self.sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.id = uuid.uuid4()
        self.ack_timeout = 5  # Tempo limite para esperar um ACK em segundos
        self.retransmitir_timeout = 2  # Tempo limite para retransmitir uma mensagem não confirmada
        self.storage = MensagemStorage()

    def enviar_mensagens_armazenadas_para_usuario(self, usuario):
        """Envia as mensagens armazenadas para um usuário específico"""
        historico_mensagens = self.storage.obter_historico_mensagens(usuario)
        for mensagem in historico_mensagens:
            mensagem_json = json.dumps(mensagem)  # Converta cada mensagem em JSON
            try:
                self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

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
                self.storage.adicionar_mensagem(endereco[0], mensagem_decodificada)  # Armazenar a mensagem no histórico do remetente
                self.enviar_ack(endereco, mensagem_id)
                self.clear_screen()
                print("Mensagens Recebidas:")
                for endereco, mensagem in self.mensagens_recebidas:
                    print(f"{endereco}: {mensagem}")
                print("\nDigite a mensagem a ser enviada:")

    def tratar_ack(self, mensagem_id):
        """Função para tratar o recebimento de um ACK"""
        pass

    def enviar_ack(self, endereco, mensagem_id):
        """Função para enviar um ACK"""
        pass

    def enviar_mensagem(self, mensagem):
        """Função para enviar uma mensagem"""
        if mensagem.strip():  # Verifica se a mensagem não está vazia
            mensagem_json = json.dumps({'id': str(uuid.uuid4()), 'mensagem': mensagem})
            for usuario in self.usuarios:
                try:
                    self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))
                except Exception as e:
                    print(f"Erro ao enviar mensagem para {usuario}: {e}")
        else:
            print("Mensagem vazia. Nada foi enviado.")

    def iniciar_chat(self):
        """Método para iniciar o chat"""
        # Envie mensagens pendentes para novos membros ao se conectar
        for usuario in self.usuarios:
            self.enviar_mensagens_armazenadas_para_usuario(usuario)

        thread_recebimento = threading.Thread(target=self.receber_mensagens)
        thread_recebimento.daemon = True
        thread_recebimento.start()

        while True:
            mensagem = input()
            self.enviar_mensagem(mensagem)

# Iniciar o chat
chat = ChatP2P()
chat.iniciar_chat()
