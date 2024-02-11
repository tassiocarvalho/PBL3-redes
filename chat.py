import socket
import threading
import os
import platform
import json
import uuid  # Importar a biblioteca uuid para gerar identificadores únicos
import time  # Importar a biblioteca time para controle de tempo

class ChatP2P:
    def __init__(self):
        self.usuarios = ["192.168.1.5", "192.168.1.14"]
        self.porta = 5111
        self.mensagens_recebidas = []
        self.sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recebimento.bind(('0.0.0.0', self.porta))
        self.sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.id = uuid.uuid4()  # Gerar um identificador único para este usuário
        self.mutex_envio = threading.Lock()  # Mutex para garantir acesso seguro ao envio de mensagens
        self.mutex_recebimento = threading.Lock()  # Mutex para garantir acesso seguro ao recebimento de mensagens

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
            with self.mutex_recebimento:
                self.mensagens_recebidas.append((endereco, mensagem_decodificada['id'], mensagem_decodificada['mensagem']))
            self.clear_screen()
            print("Mensagens Recebidas:")
            for endereco, id_mensagem, mensagem in self.mensagens_recebidas:
                print(f"{endereco}: {id_mensagem}: {mensagem}")
            print("\nDigite a mensagem a ser enviada:")

    def enviar_mensagem(self, mensagem):
        """Função para enviar uma mensagem"""
        mensagem_json = json.dumps({'id': str(self.id), 'mensagem': mensagem})
        with self.mutex_envio:
            for usuario in self.usuarios:
                try:
                    self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))
                except Exception as e:
                    print(f"Erro ao enviar mensagem para {usuario}: {e}")
        
        # Esperar por ACKs
        timeout = 3  # Tempo limite para esperar ACKs em segundos
        tempo_inicial = time.time()
        while time.time() - tempo_inicial < timeout:
            for usuario in self.usuarios:
                ack_recebido = False
                with self.mutex_recebimento:
                    for _, id_mensagem, _ in self.mensagens_recebidas:
                        if id_mensagem == str(self.id):
                            ack_recebido = True
                            break
                if not ack_recebido:
                    # Reenviar a mensagem
                    with self.mutex_envio:
                        for usuario_destino in self.usuarios:
                            try:
                                self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario_destino, self.porta))
                            except Exception as e:
                                print(f"Erro ao reenviar mensagem para {usuario_destino}: {e}")
            time.sleep(0.5)  # Esperar um curto período de tempo antes de verificar novamente

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
