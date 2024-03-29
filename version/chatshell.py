import argparse
import socket
import threading
import os
import platform
import json
import uuid
import time
from relogiolamport import RelogioLamport  # Importando a classe RelogioLamport

def get_local_ip_address(target='10.255.255.255'):
    """
    Função para obter o endereço IP local da máquina.
    Conecta-se a um endereço IP destino para determinar o endereço IP apropriado.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            # Não é necessário enviar dados, apenas iniciar a conexão
            s.connect((target, 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
    return IP
host = get_local_ip_address()

print(f"Endereço IP do host: {host}")

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
        self.usuarios = ["172.16.103.243", "172.16.103.9"]
        self.porta = 5111
        self.mensagens_recebidas = []
        self.mensagens_enviadas = []  # Adicionando inicialização da lista de mensagens enviadas
        self.sock_recebimento = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock_recebimento.bind(('0.0.0.0', self.porta))
        self.sock_envio = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.id = uuid.uuid4()
        self.ack_timeout = 5  # Tempo limite para esperar um ACK em segundos
        self.retransmitir_timeout = 2  # Tempo limite para retransmitir uma mensagem não confirmada
        self.storage = MensagemStorage()
        self.relogio_lamport = RelogioLamport()  # Criando uma instância do RelogioLamport

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

    def mensagem_enviada_pendente(self, mensagem_id):
        """Verifica se uma mensagem enviada ainda está pendente"""
        for mensagem_enviada_id, _ in self.mensagens_enviadas:
            if mensagem_enviada_id == mensagem_id:
                return True
        return False

    def receber_mensagens(self):
        """Função para receber mensagens"""
        while True:
            try:
                mensagem, endereco = self.sock_recebimento.recvfrom(4096)  # Aumentando o tamanho do buffer para evitar o erro
            except OSError as e:
                print(f"Erro ao receber mensagem: {e}")
                continue
            mensagem_decodificada = json.loads(mensagem.decode('utf-8'))
            mensagem_id = mensagem_decodificada.get('id', None)

            # Verificar se a mensagem é um ACK
            if mensagem_decodificada.get('tipo') == 'ACK' and mensagem_id:
                self.tratar_ack(mensagem_id)
            else:
                self.mensagens_recebidas.append((endereco, mensagem_decodificada['mensagem']))
                self.storage.adicionar_mensagem(endereco[0], mensagem_decodificada)  # Armazenar a mensagem no histórico do remetente
                self.relogio_lamport.sincronizar(mensagem_decodificada.get('relogio_lamport', 0))  # Sincronizar relógio de Lamport
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
        ack = json.dumps({'id': str(self.id), 'tipo': 'ACK', 'mensagem_id': mensagem_id, 'relogio_lamport': self.relogio_lamport.obter_tempo()})  # Enviar o tempo do relógio de Lamport junto com o ACK
        self.sock_envio.sendto(ack.encode('utf-8'), endereco)

    def enviar_mensagem(self, mensagem):
        """Função para enviar uma mensagem"""
        if mensagem.strip():  # Verifica se a mensagem não está vazia
            mensagem_id = str(uuid.uuid4())
            mensagem_json = json.dumps({'id': mensagem_id, 'mensagem': mensagem, 'relogio_lamport': self.relogio_lamport.obter_tempo()})  # Incluir o tempo do relógio de Lamport na mensagem
            self.relogio_lamport.incrementar()  # Incrementar o relógio de Lamport antes de enviar a mensagem
            for usuario in self.usuarios:
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
                print(f"Timeout ao aguardar pelo ACK da mensagem {mensagem_id}. Retransmitindo...")

                # Retransmitir mensagem
                while time.time() - start_time < self.ack_timeout + self.retransmitir_timeout:
                    for usuario in self.usuarios:
                        try:
                            self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))
                        except Exception as e:
                            print(f"Erro ao retransmitir mensagem para {usuario}: {e}")
                    time.sleep(0.1)  # Esperar um pouco antes de retransmitir
                else:
                    print(f"Timeout de retransmissão alcançado para a mensagem {mensagem_id}. Mensagem perdida.")
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
            parser = argparse.ArgumentParser(description='Chat P2P')
            parser.add_argument('nome', help='Nome do usuário')
            parser.add_argument('comando', help='Comando (send, read)')
            parser.add_argument('mensagem', nargs='?', default=None, help='Mensagem a ser enviada')
            args = parser.parse_args()

            if args.comando == 'send':
                self.enviar_mensagem(args.mensagem)
            elif args.comando == 'read':
                for endereco, mensagem in self.mensagens_recebidas:
                    print(f"{endereco}: {mensagem}")
            else:
                print("Comando inválido.")

# Iniciar o chat
chat = ChatP2P()
chat.iniciar_chat()