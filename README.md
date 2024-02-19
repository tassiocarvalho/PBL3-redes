# Relatório do Projeto ChatP2P

## Introdução
O projeto ChatP2P é uma aplicação de bate-papo peer-to-peer (P2P) que permite a troca de mensagens entre diferentes usuários em uma rede local. Neste relatório, vamos examinar detalhadamente a implementação do projeto, discutindo suas funcionalidades, arquitetura e componentes principais.

## Componentes Principais

### 1. Classe `MensagemStorage`
- Responsável por armazenar o histórico de mensagens de cada usuário.
- Possui métodos para adicionar mensagens ao histórico e obter o histórico de mensagens de um usuário específico.

### 2. Classe `ChatP2P`
- Gerencia toda a lógica do chat P2P, incluindo o envio e recebimento de mensagens.
- Utiliza sockets UDP para comunicação entre os usuários.
- Implementa um mecanismo de ACK (acknowledgment) para garantir a entrega das mensagens.
- Utiliza o relógio de Lamport para ordenar as mensagens.

### 3. Classe `RelogioLamport`
- Implementa o algoritmo do relógio de Lamport, que é usado para ordenar eventos em um sistema distribuído.

## Funcionalidades Principais

### Envio e Recebimento de Mensagens
- Os usuários podem enviar mensagens para outros usuários conectados.
- As mensagens são recebidas pelos destinatários e exibidas na tela.

### Acknowledgment (ACK)
- Após receber uma mensagem, o destinatário envia um ACK de volta para o remetente para confirmar o recebimento da mensagem.
- O remetente aguarda um ACK antes de considerar a mensagem entregue com sucesso.

### Armazenamento de Mensagens
- O histórico de mensagens de cada usuário é armazenado localmente.
- As mensagens são recuperadas do histórico quando um novo usuário se conecta, garantindo que eles recebam mensagens antigas.

### Relógio de Lamport
- O relógio de Lamport é utilizado para registrar o tempo dos eventos e garantir a ordenação correta das mensagens.

## Execução do Projeto
- O projeto pode ser executado diretamente a partir do código fornecido.
- Os usuários podem iniciar o chat e começar a enviar mensagens imediatamente.

## Conclusão
O projeto ChatP2P oferece uma maneira simples e eficaz de trocar mensagens entre usuários em uma rede local. Com recursos como ACK e armazenamento de mensagens, ele fornece uma experiência de bate-papo confiável e robusta. Além disso, o uso do relógio de Lamport ajuda a manter a ordem das mensagens, garantindo uma comunicação precisa entre os usuários.
