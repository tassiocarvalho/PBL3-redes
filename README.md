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

## Acknowledgment (ACK) e sua confiabilidade no Chat P2P

No chat ponto a ponto (P2P), o Acknowledgment (ACK) desempenha um papel crucial na garantia da confiabilidade da comunicação entre os nós da rede. O ACK é um tipo de mensagem de confirmação enviada por um receptor para o remetente, indicando que uma mensagem foi recebida com sucesso.

# Importância do ACK no Chat P2P:

1. **Confirmação de Recebimento:**
   Quando um nó envia uma mensagem para outro nó no chat P2P, ele aguarda a recepção de um ACK do nó de destino. Isso confirma que a mensagem foi recebida e pode ser considerada entregue com segurança.

2. **Detecção de Perda de Mensagem:**
   Se o remetente não receber um ACK dentro de um intervalo de tempo especificado, ele assume que a mensagem foi perdida no caminho. Isso desencadeia a retransmissão da mensagem para garantir que ela seja entregue ao destinatário.

3. **Garantia de Ordem de Mensagens:**
   O uso do ACK também ajuda a garantir a ordem correta das mensagens. O remetente só envia a próxima mensagem após receber o ACK da mensagem anterior, garantindo assim que as mensagens sejam exibidas na ordem correta no chat.

4. **Sincronização de Estado:**
   O ACK pode ser usado para sincronizar o estado entre os nós do chat P2P. Por exemplo, um ACK pode conter informações sobre o número de mensagens recebidas, permitindo que os nós mantenham um histórico atualizado das conversas.

Em resumo, o ACK é uma peça fundamental na arquitetura de um chat P2P, garantindo que as mensagens sejam entregues com segurança, na ordem correta e sem perdas.

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
