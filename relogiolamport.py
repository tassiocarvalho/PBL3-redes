import time

class RelogioLamport:
    def __init__(self):
        self.tempo = 0

    def incrementar(self):
        """Incrementa o relógio de Lamport em 1"""
        self.tempo += 1

    def sincronizar(self, tempo_recebido):
        """Sincroniza o relógio de Lamport com o tempo recebido, ajustando para o máximo entre os dois tempos."""
        self.tempo = max(self.tempo, tempo_recebido) + 1

    def obter_tempo(self):
        """Retorna o tempo atual do relógio de Lamport."""
        return self.tempo

    def atualizar_tempo(self, novo_tempo):
        """Atualiza o tempo do relógio de Lamport com um novo tempo, se for maior."""
        self.tempo = max(self.tempo, novo_tempo)

