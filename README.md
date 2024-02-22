# Relatório do Projeto ChatP2P

## Introdução
O projeto ChatP2P é uma aplicação de bate-papo peer-to-peer (P2P) que permite a troca de mensagens entre diferentes usuários em uma rede local. Neste relatório, vamos examinar detalhadamente a implementação do projeto, discutindo suas funcionalidades, arquitetura e componentes principais.

## Funcionamento do Chat P2P

### Envio de Mensagens para Todos os Membros da Lista de IPs

- O chat P2P envia mensagens para todos os membros da lista de IPs especificados no código. Isso permite que cada membro receba as mensagens enviadas por outros membros em tempo real.

### Uso do Relógio de Lamport para Ordenação

- Para garantir a ordenação correta das mensagens, o chat P2P utiliza o Relógio de Lamport. Este relógio lógico é uma ferramenta essencial para sincronizar eventos em um ambiente distribuído, como o chat P2P. Ele é utilizado para marcar cada mensagem com um carimbo de tempo, permitindo que os nós recebam e exibam as mensagens na ordem correta, mesmo que elas tenham sido enviadas em momentos diferentes.

### Utilização do ACK para Confirmação de Recebimento

- O chat P2P faz uso do ACK (Acknowledgment) para garantir a confiabilidade da comunicação. Após receber uma mensagem, um nó envia um ACK de volta para o remetente, confirmando que a mensagem foi recebida com sucesso. Isso garante que as mensagens sejam entregues de forma segura e que o remetente tenha conhecimento do recebimento por parte do destinatário.

Com essa combinação de envio de mensagens para todos os membros da lista de IPs, utilização do Relógio de Lamport para ordenação e uso do ACK para confirmação de recebimento, o chat P2P proporciona uma experiência de comunicação confiável e em tempo real entre os membros da rede.

## Componentes Principais

### 1. Classe `MensagemStorage`
- Responsável por armazenar o histórico de mensagens de cada usuário.
- Possui métodos para adicionar mensagens ao histórico e obter o histórico de mensagens de um usuário específico.

### 2. Classe `ChatP2P`
- Gerencia toda a lógica do chat P2P, incluindo o envio e recebimento de mensagens.
- Utiliza sockets UDP para comunicação entre os usuários.
- Implementa um mecanismo de ACK (acknowledgment) para garantir a entrega das mensagens.
- Utiliza o relógio de Lamport para ordenar as mensagens.

## Funcionalidades Principais

### Envio e Recebimento de Mensagens
- Os usuários podem enviar mensagens para outros usuários conectados.
- As mensagens são recebidas pelos destinatários e exibidas na tela.

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

## Criando e Executando a Build do Chat P2P

### Pré-requisitos

Certifique-se de ter o Docker instalado em sua máquina antes de prosseguir.

### Criando a Build

1. Clone o repositório do Chat P2P em sua máquina local:

   ```bash
   git clone <https://github.com/tassiocarvalho/PBL3-redes.git>
   ```

2. Navegue até o diretório onde o repositório foi clonado:

   ```bash
   cd chat-p2p
   ```

3. Agora, crie a build do chat P2P usando o Docker:

   ```bash
   docker build -t chat .
   ```

### Executando a Aplicação

1. Após a construção da imagem Docker, execute o seguinte comando para iniciar a aplicação:

   ```bash
   docker run -it --network host chat
   ```

2. Agora você está pronto para usar o chat P2P! Siga as instruções fornecidas no console para selecionar um usuário para sincronização e começar a trocar mensagens.

Com esses passos simples, você será capaz de criar e executar o chat P2P em sua máquina usando o Docker.

## Conclusão
O projeto ChatP2P oferece uma maneira simples e eficaz de trocar mensagens entre usuários em uma rede local. Com recursos como ACK e armazenamento de mensagens, ele fornece uma experiência de bate-papo confiável. Além disso, o uso do relógio de Lamport ajuda a manter a ordem das mensagens, garantindo uma comunicação precisa entre os usuários. No entanto, para uma melhor experiência, o projeto pode se beneficiar de algumas melhorias, como uma interface de usuário mais amigável e uma gestão mais robusta de conexões e erros de rede. Essas melhorias podem tornar o ChatP2P ainda mais acessível e confiável para os usuários.
