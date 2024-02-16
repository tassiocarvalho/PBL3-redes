# Usar uma imagem oficial do Python como base
FROM python:3.9-slim

# Definir o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copiar o código-fonte do projeto para o contêiner
COPY . .

# Instalar as dependências do Python
RUN pip install --no-cache-dir gunicorn

# Expor a porta utilizada pelo seu aplicativo
EXPOSE 5111

# Executar o programa Python
CMD ["python", "chat.py"]
