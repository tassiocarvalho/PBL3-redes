#!/bin/bash

# Verifica se o número de argumentos está correto
if [ $# -lt 2 ]; then
    echo "Uso: $0 <nome> <comando> [<mensagem>]"
    exit 1
fi

# Nome do usuário
NOME=$1

# Comando (send ou read)
COMANDO=$2

# Mensagem (se houver)
MENSAGEM=$3

# Caminho para o script Python
PYTHON_SCRIPT="chatsheell.py"

# Executa o script Python com os argumentos apropriados
if [ "$COMANDO" == "send" ]; then
    python3 $PYTHON_SCRIPT $NOME $COMANDO "$MENSAGEM"
elif [ "$COMANDO" == "read" ]; then
    python3 $PYTHON_SCRIPT $NOME $COMANDO
else
    echo "Comando inválido. Use 'send' para enviar uma mensagem ou 'read' para ler as mensagens recebidas."
fi
