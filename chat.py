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
        self.timeout = 5  # Tempo limite em segundos
        self.max_retransmissoes = 3  # Número máximo de retransmissões

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
            if mensagem_decodificada['id'] not in [msg['id'] for _, msg in self.mensagens_recebidas]:
                self.mensagens_recebidas.append((endereco, mensagem_decodificada))
                self.enviar_ack(mensagem_decodificada['id'], endereco)

            self.clear_screen()
            print("Mensagens Recebidas:")
            for endereco, mensagem in self.mensagens_recebidas:
                print(f"{endereco}: {mensagem['mensagem']}")
            print("\nDigite a mensagem a ser enviada:")

    def enviar_ack(self, id_mensagem, endereco_destino):
        """Função para enviar um ACK para o remetente"""
        mensagem_ack = json.dumps({'ack': id_mensagem})
        self.sock_envio.sendto(mensagem_ack.encode('utf-8'), endereco_destino)

    def enviar_mensagem(self, mensagem):
        """Função para enviar uma mensagem"""
        mensagem_json = json.dumps({'id': str(self.id), 'mensagem': mensagem})
        seq_num = 0  # Número de sequência da mensagem
        tentativas = 0  # Contador de tentativas de envio
        while tentativas < self.max_retransmissoes:
            try:
                self.sock_envio.sendto(mensagem_json.encode('utf-8'), (self.usuarios[0], self.porta))
                inicio = time.time()  # Tempo inicial
                while True:
                    mensagem, endereco = self.sock_recebimento.recvfrom(1024)
                    mensagem_decodificada = json.loads(mensagem.decode('utf-8'))
                    if 'ack' in mensagem_decodificada and mensagem_decodificada['ack'] == str(self.id):
                        print("ACK recebido com sucesso.")
                        return  # ACK recebido, encerrar envio
                    elif time.time() - inicio > self.timeout:
                        break  # Tempo limite atingido
                tentativas += 1
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")
        print("Número máximo de retransmissões alcançado. Mensagem não enviada.")

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
