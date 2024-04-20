import os
from datetime import datetime
from twilio.rest import Client
import pandas as pd
from dotenv import load_dotenv

# Load Environment Variables
load_dotenv()

# Configurações da conta Twilio
client = Client(os.getenv("ACCOUNT_SID"), os.getenv("AUTH_TOKEN"))


# Função para ler dados do arquivo CSV
def ler_dados_csv():

    data = datetime.now()

    # Caminho absoluto do arquivo
    absolute_path = fr"D:\felip\Documents Felipe\Lista Van\automate-list-of-passengers\lista_passageiros\lista_passageiros_{data.strftime('%Y-%m-%d')}.csv"

    # Diretório de partida (onde você estará executando o script)
    starting_directory = os.getcwd()

    # Caminho relativo do arquivo em relação ao diretório de partida
    relative_path = os.path.relpath(absolute_path, starting_directory)

    df = pd.read_csv(relative_path, sep=',', encoding='UTF-8', on_bad_lines='skip', header=0)

    return df


def tratamento_dos_dados(df) -> str:

    # Remover linhas onde "VAI OU NÃO VAI" é igual a "NÃO VOU"
    df = df[df['VAI OU NÃO VAI'] != 'NÃO VOU']

    # Substituir NaN por uma string vazia
    df.fillna('', inplace=True)

    vai = []
    volta = []
    # Iterar sobre cada linha para gerar o txt
    for index, row in df.iterrows():
        passageiro = row['NOME DO PASSAGEIRO']
        ponto_encontro = row['PONTO DE ENCONTRO']
        resposta = row['VAI OU NÃO VAI']

        if resposta != 'SÓ VOLTO':
            linha_txt = f'- {passageiro} {f"({ponto_encontro}) " if ponto_encontro != "" else ""}=> *{resposta}* \n'
            if resposta != 'NÃO RESPONDEU':
                linha_txt = linha_txt.split('=>', maxsplit=1)[0] + "\n"
            vai.append(linha_txt)
        else:
            linha_txt = f'- {passageiro} {f"({ponto_encontro}) " if ponto_encontro != "" else ""} \n'
            volta.append(linha_txt)

    mensagem = (f'*_IRÃO HOJE {datetime.now().day}/{datetime.now().month}_*\n\n'
                f'*Placa da van:* DXB5B96\n\n'
                f'*VAI:* \n\n{"".join(vai)}\n'
                f'*SÓ VOLTA:* \n\n{"".join(volta)}')

    return mensagem


# Função para enviar mensagem pelo WhatsApp para um grupo
def enviar_mensagem_grupo_whatsapp(grupo: str, mensagem: str):

    numeros_destino = ['+5511964034305', '+5512988675254']

    for numero in numeros_destino:

        message = client.messages.create(
                                  from_='whatsapp:+14155238886',
                                  body=mensagem,
                                  to=f'whatsapp:{numero}'
                              )

    print(f'Mensagem enviada para o grupo {grupo} com sucesso!')
