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
        self.numero_sequencia = 0  # Número de sequência para controle de ACKs
        self.mensagens_enviadas = {}  # Dicionário para rastrear mensagens enviadas
        self.timeout = 5  # Tempo limite para aguardar um ACK

    def clear_screen(self):
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    def receber_mensagens(self):
        while True:
            mensagem, endereco = self.sock_recebimento.recvfrom(1024)
            mensagem_decodificada = json.loads(mensagem.decode('utf-8'))
            if 'mensagem' in mensagem_decodificada:
                self.mensagens_recebidas.append((endereco, mensagem_decodificada['mensagem']))
                self.clear_screen()
                print("Mensagens Recebidas:")
                for endereco, mensagem in self.mensagens_recebidas:
                    print(f"{endereco}: {mensagem}")
                print("\nDigite a mensagem a ser enviada:")
            elif 'ack' in mensagem_decodificada:
                ack_numero_sequencia = mensagem_decodificada['ack']
                # Remover a mensagem enviada correspondente do registro
                self.mensagens_enviadas.pop(ack_numero_sequencia, None)

    def enviar_mensagem(self, mensagem):
        numero_sequencia_atual = self.numero_sequencia
        mensagem_json = json.dumps({'id': str(self.id), 'numero_sequencia': numero_sequencia_atual, 'mensagem': mensagem})
        for usuario in self.usuarios:
            try:
                self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))
                # Armazenar a mensagem enviada no registro
                self.mensagens_enviadas[numero_sequencia_atual] = {'mensagem': mensagem, 'timestamp': time.time()}  # Armazenar número de sequência e mensagem
                self.numero_sequencia += 1
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

    def verificar_ack(self):
        while True:
            # Verificar mensagens enviadas sem ACK
            for numero_sequencia, mensagem in list(self.mensagens_enviadas.items()):  # Convertendo para lista para evitar modificações durante a iteração
                if time.time() - mensagem['timestamp'] > self.timeout:
                    self.enviar_mensagem(mensagem['mensagem'])  # Retransmitir mensagem
            time.sleep(1)

    def iniciar_chat(self):
        thread_recebimento = threading.Thread(target=self.receber_mensagens)
        thread_recebimento.daemon = True
        thread_recebimento.start()

        thread_verificar_ack = threading.Thread(target=self.verificar_ack)
        thread_verificar_ack.daemon = True
        thread_verificar_ack.start()

        while True:
            mensagem = input()
            self.enviar_mensagem(mensagem)

# Iniciar o chat
chat = ChatP2P()
chat.iniciar_chat()
