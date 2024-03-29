import socket
import threading
import os
import platform
import json
import uuid
import time
import random 
from relogiolamport import RelogioLamport  # Importando a classe RelogioLamport

def get_local_ip_address():
    """
    Função para obter o endereço IP local da máquina hospedeira.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            # Conecta-se a um endereço IP externo para determinar o endereço IP local
            s.connect(('8.8.8.8', 80))
            ip_address = s.getsockname()[0]
        except Exception:
            ip_address = '127.0.0.1'
    return ip_address
    #up

host = get_local_ip_address()
print("Endereço IP do host:", host)

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
        """Retorna o histórico de mensagens do usuário"""
        return self.historico_mensagens.get(usuario, [])

class ChatP2P:
    def __init__(self):
        self.usuarios = ["172.16.103.243", "172.16.103.1", "172.16.103.2", "172.16.103.3", "172.16.103.4",
        "172.16.103.5", "172.16.103.6","172.16.103.7", "172.16.103.8","172.16.103.9", "172.16.103.10", 
        "172.16.103.11","172.16.103.12", "172.16.103.13", "172.16.103.14",]
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
    
    frases_aleatorias = [
        "A vida é uma jornada, não um destino.",
        "O sucesso é a soma de pequenos esforços repetidos dia após dia.",
        "Se você quer algo que nunca teve, precisa fazer algo que nunca fez.",
        "A persistência é o caminho do êxito.",
        "Quanto maior o obstáculo, mais glória em superá-lo."
    ]

    def sincronizar_com_usuario(self, usuario_sincronizacao):
        """Método para sincronizar com um usuário específico"""
        mensagem_solicitacao = json.dumps({'tipo': 'SOLICITACAO_HISTORICO', 'id': str(self.id)})
        self.sock_envio.sendto(mensagem_solicitacao.encode('utf-8'), (usuario_sincronizacao, self.porta))
        print("Solicitação de histórico enviada para", usuario_sincronizacao)

        # Aguardar pelo histórico de mensagens
        start_time = time.time()
        while time.time() - start_time < self.ack_timeout:
            if usuario_sincronizacao in self.storage.historico_mensagens:
                print("Histórico recebido:")
                for mensagem in self.storage.historico_mensagens[usuario_sincronizacao]:
                    print(mensagem)
                break
            time.sleep(0.1)
        else:
            print("Timeout ao aguardar pelo histórico de mensagens para", usuario_sincronizacao)


    def enviar_historico_mensagens(self, endereco, mensagem):
        """Envia o histórico de mensagens para o endereço especificado"""
        usuario = endereco[0]
        historico_mensagens = self.storage.obter_historico_mensagens(usuario)
        mensagem_historico = {'tipo': 'HISTORICO', 'historico': historico_mensagens}
        mensagem_json = json.dumps(mensagem_historico)
        try:
            self.sock_envio.sendto(mensagem_json.encode('utf-8'), endereco)
            print("Histórico de mensagens enviado para", endereco)
        except Exception as e:
            print(f"Erro ao enviar histórico de mensagens para {endereco}: {e}")

    def enviar_historico_completo(self, endereco, mensagem):
        """Envia todo o histórico de mensagens para o endereço especificado"""
        usuario = endereco[0]
        historico_mensagens = self.storage.historico_mensagens  # Obter todo o histórico de mensagens
        mensagem_historico = {'tipo': 'HISTORICO_COMPLETO', 'historico': historico_mensagens.get(usuario, [])}
        mensagem_json = json.dumps(mensagem_historico)
        try:
            self.sock_envio.sendto(mensagem_json.encode('utf-8'), endereco)
            print("Histórico completo de mensagens enviado para", endereco)
        except Exception as e:
            print(f"Erro ao enviar histórico completo de mensagens para {endereco}: {e}")

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

    def salvar_historico_mensagens(self):
        """Salva o histórico de mensagens em um arquivo de texto"""
        with open("historico_mensagens.txt", "w") as file:
            for endereco, mensagem in self.mensagens_recebidas:
                file.write(f"{endereco}: {mensagem}\n")
        print("Histórico de mensagens salvo em 'historico_mensagens.txt'.")

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
            tipo_mensagem = mensagem_decodificada.get('tipo', None)

            # Verificar se a mensagem é um ACK
            if tipo_mensagem == 'ACK' and mensagem_id:
                self.tratar_ack(mensagem_id)
            elif tipo_mensagem == 'SOLICITACAO_HISTORICO':
                # Lógica para responder à solicitação de histórico de mensagens
                self.enviar_historico_completo(endereco, mensagem_decodificada)
            else:
                # Processar a mensagem recebida
                if 'mensagem' in mensagem_decodificada:  # Verificar se a chave 'mensagem' está presente
                    self.mensagens_recebidas.append((endereco, mensagem_decodificada['mensagem']))
                    self.storage.adicionar_mensagem(endereco[0], mensagem_decodificada)  # Armazenar a mensagem no histórico do remetente
                    self.relogio_lamport.sincronizar(mensagem_decodificada.get('relogio_lamport', 0))  # Sincronizar relógio de Lamport
                    self.enviar_ack(endereco, mensagem_id)
                    self.clear_screen()
                    print("Mensagens Recebidas:")
                    for endereco, mensagem in self.mensagens_recebidas:
                        print(f"{endereco}: {mensagem}")
                    print("\nDigite a mensagem a ser enviada:")
                elif tipo_mensagem == 'HISTORICO':
                    # Receber e armazenar o histórico de mensagens
                    historico = mensagem_decodificada.get('historico', [])
                    for msg in historico:
                        self.storage.adicionar_mensagem(endereco[0], msg)
                    print("Histórico de mensagens recebido de", endereco)
                else:
                    print("Mensagem recebida não possui o campo 'mensagem'.")

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
        if mensagem.strip() == "/salvar":  # Verifica se o comando é "/salvar"
            self.salvar_historico_mensagens()  # Chama o método para salvar o histórico de mensagens
        else:
            if mensagem.strip():  # Verifica se a mensagem não está vazia
                if mensagem.strip() == "/10":  # Verifica se a mensagem é o comando "/10"
                    for _ in range(100):
                        mensagem_aleatoria = random.choice(self.frases_aleatorias)
                        mensagem_id = str(uuid.uuid4())
                        mensagem_json = json.dumps({'id': mensagem_id, 'mensagem': mensagem_aleatoria, 'relogio_lamport': self.relogio_lamport.obter_tempo()})
                        self.relogio_lamport.incrementar()
                        for usuario in self.usuarios:
                            try:
                                self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))
                            except Exception as e:
                                print(f"Erro ao enviar mensagem para {usuario}: {e}")
                else:
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


    def enviar_mensagens_armazenadas_para_usuario(self, usuario):
        """Envia as mensagens armazenadas para um usuário específico"""
        historico_mensagens = self.storage.obter_historico_mensagens(usuario)
        for mensagem in historico_mensagens:
            mensagem_json = json.dumps(mensagem)  # Converta cada mensagem em JSON
            try:
                self.sock_envio.sendto(mensagem_json.encode('utf-8'), (usuario, self.porta))
            except Exception as e:
                print(f"Erro ao enviar mensagem para {usuario}: {e}")

    def iniciar_chat(self):
        """Método para iniciar o chat"""
        # Selecionar o usuário para sincronização
        print("Escolha um usuário que esteja online, se não há nenhum escolha a si mesmo")
        for i, usuario in enumerate(self.usuarios, 1):
            print(f"{i}. {usuario}")
        usuario_selecionado = int(input("Selecione o número do usuário para sincronização: "))
        usuario_sincronizacao = self.usuarios[usuario_selecionado - 1]

        # Sincronização de 5 segundos com o usuário selecionado
        print(f"Sincronizando com {usuario_sincronizacao}...")
        time.sleep(5)
        print("Sincronização concluída. Iniciando o chat.")

        self.sincronizar_com_usuario(usuario_sincronizacao)

        # Envie mensagens pendentes apenas para o usuário selecionado
        self.enviar_mensagens_armazenadas_para_usuario(usuario_sincronizacao)

        # Iniciar a thread de recebimento de mensagens
        thread_recebimento = threading.Thread(target=self.receber_mensagens)
        thread_recebimento.daemon = True
        thread_recebimento.start()

        # Loop para enviar mensagens
        while True:
            mensagem = input()
            self.enviar_mensagem(mensagem)


# Iniciar o chat
chat = ChatP2P()
chat.iniciar_chat()