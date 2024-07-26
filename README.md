# Previsão do Tempo Diário

## Descrição
O projeto Previsão do Tempo Diário é um sistema automatizado para coletar e enviar previsões do tempo por e-mail. Ele realiza web scraping do site tempo.com para obter dados meteorológicos e envia um e-mail diário com a previsão do tempo atual e para os próximos três dias.

## Funcionalidades
- **Extração de Dados Meteorológicos**: Coleta informações sobre temperatura atual, previsão para os próximos 3 dias, probabilidade e quantidade de chuva, e dados sobre ventos.
- **Envio de E-mail**: Envia um e-mail formatado com HTML e estilos CSS contendo a previsão do tempo para o destinatário especificado.
- **Agendamento**: Utiliza a biblioteca `schedule` para enviar e-mails diariamente às 07:00.

## Tecnologias Utilizadas
- **Linguagem**: Python
- **Bibliotecas**:
  - `BeautifulSoup` para web scraping.
  - `Requests` para requisições HTTP.
  - `smtplib` para envio de e-mails.
  - `schedule` para agendamento de tarefas.
  - `python-dotenv` para gerenciamento de variáveis de ambiente.
  - `logging` para registro de logs.

## Requisitos
- Python 3.x
- Instale as dependências com:
  ```bash
  pip install beautifulsoup4 requests python-dotenv schedule

## Observações

- **Credenciais de E-mail**: Certifique-se de que as credenciais do e-mail estão corretas e que o acesso ao servidor SMTP do Gmail está permitido.
- **E-mail do Destinatário**: O endereço de e-mail do destinatário está definido no código. Altere o valor da variável `destinatario` para o e-mail desejado.
- **Conexão com a Internet**: O script depende de uma conexão com a internet para acessar o site de previsão do tempo e enviar e-mails.
