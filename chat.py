import socket
import threading
import os
import platform
import json
import uuid  # Importar a biblioteca uuid para gerar identificadores únicos

class ChatP2P:
    def __init__(self):
        self.usuarios = ["192.168.1.5", "192.168.1.14"]
        self.porta = 5111
        self.mensagens_recebidas = []
        self.sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recebimento.bind(('0.0.0.0', self.porta))
        self.sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.id = uuid.uuid4()  # Gerar um identificador único para este usuário
        self.ack_recebidos = {}  # Dicionário para armazenar ACKs recebidos

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

            # Verificar se é uma mensagem de ACK
            if 'ack' in mensagem_decodificada:
                mensagem_id = mensagem_decodificada['ack']
                if mensagem_id in self.ack_recebidos:
                    # Remover o ACK da lista de ACKs pendentes
                    del self.ack_recebidos[mensagem_id]

            else:
                # Adicionar mensagem recebida à lista
                self.mensagens_recebidas.append((endereco, mensagem_decodificada['mensagem']))
                self.clear_screen()
                print("Mensagens Recebidas:")
                for endereco, mensagem in self.mensagens_recebidas:
                    print(f"{endereco}: {mensagem}")
                print("\nDigite a mensagem a ser enviada:")

                # Enviar ACK para o remetente
                ack_message = json.dumps({'ack': mensagem_decodificada['id']})
                self.sock_envio.sendto(ack_message.encode('utf-8'), endereco)

    def enviar_mensagem(self, mensagem):
        """Função para enviar uma mensagem"""
        mensagem_json = json.dumps({'id': str(self.id), 'mensagem': mensagem})
        mensagem_id = str(uuid.uuid4())  # Gerar um ID único para a mensagem
        mensagem_json_com_id = json.dumps({'id': mensagem_id, 'mensagem': mensagem})
        for usuario in self.usuarios:
            try:
                self.sock_envio.sendto(mensagem_json_com_id.encode('utf-8'), (usuario, self.porta))
                # Adicionar o ID da mensagem aos ACKs pendentes
                self.ack_recebidos[mensagem_id] = True
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
