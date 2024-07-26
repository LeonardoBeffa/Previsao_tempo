from email.message import EmailMessage
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import logging
import requests
import schedule
import smtplib
import time
import os
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
load_dotenv()
os.system('cls')

def probi_chuva(cont):
    try:
        prob_chuva = cont.find('span', class_='txt-strng probabilidad center').get_text()
        qtd_chuva = cont.find('span', class_='changeUnitR').get_text()
        return prob_chuva, qtd_chuva
    except:
        return 0, 0

def ventos(cont):
    try:
        vento_min = cont.find('span', class_='changeUnitW').get_text()
        vento_max = cont.find('span', class_='changeUnitW').find_next_sibling('span').get_text()
        return vento_max, vento_min
    except:
        return 0, 0

def temp_atual(soup):
    try:
        temp_atual = soup.find('span', class_='dato-temperatura changeUnitT').get_text()
        return temp_atual
    except:
        return None

def extrair_dados():
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, como Gecko) Chrome/124.0.0.0 Safari/537.36"}
    url = 'https://www.tempo.com/campo-mourao.htm'
    site = requests.get(url, headers=headers)
    soup = BeautifulSoup(site.content, 'html.parser')
    content = soup.find_all('li', class_=re.compile('grid-item dia'))

    data_hj = datetime.now().strftime("%d")
    previ_prox_3_dias = []
    
    logging.info("Extraindo Dados...")
    
    for cont in content[:4]: 
        tempo = cont.find('img', class_='simbW').get('alt')
        day = cont.find('span', class_='subtitle-m').get_text()
        day_temp = day.split()
        temp_max = cont.find('span', class_='max changeUnitT').get_text()
        temp_min = cont.find('span', class_='min changeUnitT').get_text()
        
        vento_max, vento_min = ventos(cont)
        prob_chuva, qtd_chuva = probi_chuva(cont)
        
        if day_temp[0] in data_hj:
            atual = temp_atual(soup)
            dados_hoje = {
                'day': day,
                'atual': atual,
                'tempo': tempo,
                'temp_max': temp_max,
                'temp_min': temp_min,
                'vento_max': vento_max,
                'vento_min': vento_min,
                'prob_chuva': prob_chuva,
                'qtd_chuva': qtd_chuva
            }
        else:
            dados_1 = f'\nData: {day} \nTempo: {tempo}. \nTemperatura Máxima: {temp_max} Mínima: {temp_min}'
            dados_2 = f'Probabilidade de Chuva: {prob_chuva} Quantidade de Chuva: {qtd_chuva}'
            dados_3 = f'Ventos: {vento_max} a {vento_min} km/h'
            previ_prox_3_dias.append(f'{dados_1}\n{dados_2}\n{dados_3}')
    
    if 'dados_hoje' in locals():
        logging.info('Dados Extraidos com Sucesso.!')
        return dados_hoje, previ_prox_3_dias
    else:
        logging.info('Dados Extraidos com Sucesso.!')
        return None, previ_prox_3_dias

def enviar_email(destinatario, dados_hoje, previ_prox_3_dias, cidade):
    logging.info('Criando o email com essas informações...')
    EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        raise EnvironmentError("Variáveis de ambiente não foram definidas")

    mail = EmailMessage()
    mail['Subject'] = 'Previsão do tempo'
    mail['From'] = EMAIL_ADDRESS
    mail['To'] = destinatario

    mensagem_prox_3_dias = '<div class="bloco-interno"><h2>Previsão para os Próximos 3 Dias</h2>'
    for dados in previ_prox_3_dias:
        mensagem_prox_3_dias += f'<p>{dados}</p>'
    mensagem_prox_3_dias += '</div>'

    mensagem_hoje = f"""
    <div class="bloco-principal">
        <h2>Previsão do Tempo Hoje para a Cidade de {cidade}</h2>
        <div class="data-temp">
            <p>Data: {dados_hoje['day']} Temperatura Atual: </p>
            <p>{dados_hoje['atual']}</p>
        </div>
        <div class="informacoes">
            <div class="temp-vento">
                <div class="temp">
                    <p>Temperatura Máxima: {dados_hoje['temp_max']}</p>
                    <p>Temperatura Mínima: {dados_hoje['temp_min']}</p>
                </div>
                <div class="vento">
                    <p>Vento Máximo: {dados_hoje['vento_max']} km/h</p>
                    <p>Vento Mínimo: {dados_hoje['vento_min']} km/h</p>
                </div>
            </div>
        </div>
        <p>Tempo: {dados_hoje['tempo']}</p>
        {f'<p>Probabilidade de Chuva: {dados_hoje["prob_chuva"]}</p><p>Quantidade de Chuva: {dados_hoje["qtd_chuva"]}</p>' if dados_hoje['prob_chuva'] else ''}
        {mensagem_prox_3_dias}
    </div>
    """

    mensagem = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
            }}
            .bloco-principal {{
                background-color: #333333; /* Cinza escuro */
                color: white;
                padding: 10px;
                margin: 20px 0;
                border-radius: 8px;
                border: 3px solid black; /* Borda preta */
                display: inline-block; /* Ajusta o tamanho do bloco ao conteúdo */
                max-width: 100%; /* Evita que o bloco se estenda além da largura da tela */
            }}
            .bloco-interno {{
                background-color: #333333; /* Cinza escuro */
                color: white;
                padding: 10px;
                margin-top: 10px;
                border-radius: 8px;
                border: 3px solid black; /* Borda preta */
                display: inline-block; /* Ajusta o tamanho do bloco ao conteúdo */
                max-width: 100%; /* Evita que o bloco se estenda além da largura da tela */
            }}
            .data-temp {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 10px;
            }}
            .data-temp p {{
                margin: 0;
            }}
            .informacoes {{
                display: flex;
                flex-direction: column;
            }}
            .temp-vento {{
                display: flex;
                justify-content: space-between;
            }}
            .temp, .vento {{
                flex: 1;
            }}
            .vento {{
                margin-left: 10px;
            }}
            .temp p, .vento p {{
                margin: 0;
            }}
        </style>
    </head>
    <body>
        {mensagem_hoje}
    </body>
    </html>
    """

    mail.add_header('Content-Type', 'text/html')
    mail.set_payload(mensagem.encode('utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(mail)
        logging.info('Email enviado com sucesso!')

def agendar_email():
    #programado para executar todos os dias as 7h da manha.
    schedule.every().day.at('07:00').do(executar_prog)

def executar_prog():
    cidade = 'Campo Mourão.'
    dados_hoje, previ_prox_3_dias = extrair_dados()
    if dados_hoje:
        
        #Altere para o Email Desejado.
        destinatario = os.getenv('EMAIL_ADDRESS')
        
        enviar_email(destinatario, dados_hoje, previ_prox_3_dias, cidade)
    else:
        logging.info("Não foi possível obter a previsão do tempo.")

if __name__ == "__main__":
    logging.info('Iniciando o Programa! Aguarde...')
    
    load_dotenv()    
    agendar_email()

    while True:
        schedule.run_pending()
        time.sleep(1)
        logging.info('Aguardando até o proximo Envio...')