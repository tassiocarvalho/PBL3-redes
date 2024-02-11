import socket
import threading
import os
import platform
import json
import uuid
import time

class MensagemStorage:
    def __init__(self):
        self.mensagens_por_usuario = {}  # Dicionário para armazenar mensagens por usuário

    def adicionar_mensagem(self, usuario, mensagem):
        if usuario not in self.mensagens_por_usuario:
            self.mensagens_por_usuario[usuario] = []
        self.mensagens_por_usuario[usuario].append(mensagem)

    def obter_mensagens(self, usuario):
        return self.mensagens_por_usuario.get(usuario, [])

class ChatP2P:
    def __init__(self):
        self.usuarios = ["192.168.1.5", "192.168.1.14"]
        self.porta = 5111
        self.mensagens_recebidas = []
        self.mensagens_enviadas = []  # Adicionando inicialização da lista de mensagens enviadas
        self.sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recebimento.bind(('0.0.0.0', self.porta))
        self.sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.id = uuid.uuid4()
        self.ack_timeout = 5  # Tempo limite para esperar um ACK em segundos
        self.storage = MensagemStorage()

    def clear_screen(self):
        """Função para limpar a tela de forma multiplataforma"""
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    def mensagem_enviada_pendente(self, mensagem_id):
        """Verifica se uma mensagem enviada ainda está pendente"""
        for mensagem_enviada_id, _ in self.mensagens_enviadas:
            if mensagem_enviada_id == mensagem_id:
                return True
        return False

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
        for index, (mensagem_enviada_id, _) in enumerate(self.mensagens_enviadas):
            if mensagem_enviada_id == mensagem_id:
                del self.mensagens_enviadas[index]
                break

    def enviar_ack(self, endereco, mensagem_id):
        """Função para enviar um ACK"""
        ack = json.dumps({'id': str(self.id), 'tipo': 'ACK', 'mensagem_id': mensagem_id})
        self.sock_envio.sendto(ack.encode('utf-8'), endereco)

    def enviar_mensagem(self, mensagem):
        """Função para enviar uma mensagem"""
        mensagem_id = str(uuid.uuid4())
        mensagem_json = json.dumps({'id': mensagem_id, 'mensagem': mensagem})
        for usuario in self.usuarios:
            self.storage.adicionar_mensagem(usuario, mensagem_json)  # Armazenar a mensagem para o usuário
            try:
                self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

        # Aguardar pelo ACK
        start_time = time.time()
        while time.time() - start_time < self.ack_timeout:
            if not self.mensagem_enviada_pendente(mensagem_id):
                break
            time.sleep(0.1)  # Esperar um pouco antes de verificar novamente
        else:
            print("Timeout ao aguardar pelo ACK")

    def iniciar_chat(self):
        """Método para iniciar o chat"""
        # Envie mensagens pendentes para novos membros ao se conectar
        for usuario in self.usuarios:
            for mensagem_json in self.storage.obter_mensagens(usuario):
                self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))

        thread_recebimento = threading.Thread(target=self.receber_mensagens)
        thread_recebimento.daemon = True
        thread_recebimento.start()

        while True:
            mensagem = input()
            self.enviar_mensagem(mensagem)

# Iniciar o chat
chat = ChatP2P()
chat.iniciar_chat()
