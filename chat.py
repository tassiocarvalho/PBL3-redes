import socket
import threading
import os
import platform
import json
import uuid  # Importar a biblioteca uuid para gerar identificadores únicos
import time

class ChatP2P:
    def __init__(self):
        self.usuarios = ["192.168.1.5", "192.168.1.14"]
        self.porta = 5111
        self.mensagens_recebidas = []
        self.sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recebimento.bind(('0.0.0.0', self.porta))
        self.sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.id = uuid.uuid4()  # Gerar um identificador único para este usuário
        self.acks_recebidos = {}  # Dicionário para rastrear os ACKs recebidos
        self.timeout = 5  # Tempo limite para aguardar ACKs (em segundos)

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
            # Adicionar ACK recebido ao dicionário de ACKs recebidos
            if 'ack' in mensagem_decodificada:
                self.acks_recebidos[mensagem_decodificada['ack']] = True
            else:
                self.mensagens_recebidas.append((endereco, mensagem_decodificada['id'], mensagem_decodificada['mensagem']))
                self.clear_screen()
                print("Mensagens Recebidas:")
                for endereco, id_mensagem, mensagem in self.mensagens_recebidas:
                    print(f"{endereco} - ID: {id_mensagem}: {mensagem}")
                print("\nDigite a mensagem a ser enviada:")

    def enviar_mensagem(self, mensagem):
        """Função para enviar uma mensagem"""
        mensagem_json = json.dumps({'id': str(self.id), 'mensagem': mensagem})
        for usuario in self.usuarios:
            try:
                self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))
                print(f"Mensagem enviada para {usuario}: {mensagem}")
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

    def verificar_acks(self):
        """Função para verificar os ACKs recebidos"""
        while True:
            # Verificar se todos os ACKs foram recebidos para as mensagens enviadas
            for id_mensagem in self.acks_recebidos:
                if not self.acks_recebidos[id_mensagem]:
                    # Reenviar a mensagem
                    for usuario in self.usuarios:
                        try:
                            mensagem_json = json.dumps({'id': id_mensagem, 'mensagem': ''})  # Enviar mensagem vazia
                            self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))
                            print(f"Mensagem reenviada para {usuario} (ID: {id_mensagem})")
                        except Exception as e:
                            print(f"Erro ao reenviar mensagem para {usuario}: {e}")
            time.sleep(self.timeout)  # Esperar pelo tempo limite para verificar ACKs novamente

    def iniciar_chat(self):
        """Método para iniciar o chat"""
        thread_recebimento = threading.Thread(target=self.receber_mensagens)
        thread_recebimento.daemon = True
        thread_recebimento.start()

        thread_verificar_acks = threading.Thread(target=self.verificar_acks)
        thread_verificar_acks.daemon = True
        thread_verificar_acks.start()

        while True:
            mensagem = input()
            self.enviar_mensagem(mensagem)

# Iniciar o chat
chat = ChatP2P()
chat.iniciar_chat()
