from __future__ import annotations
import pathlib
from datetime import datetime
from typing import Dict
import pandas as pd


# Dicionário dos passageiros da van
passageiros: Dict[str, Dict[str, str]] = {

    "Marcos Camargo": {

        'nome_itinerario': 'Marcos Camargo',
        'ponto_encontro': 'ehma',
        'telefone': 5512988276924

    },

    # 'Tauane Santos': {
    #
    #     'nome_itinerario': 'Tauane Santos',
    #     'ponto_encontro': 'Jd.Rep',
    #     'telefone': None
    #
    # },

    "Camila Costa": {

        'nome_itinerario': 'Camila Costa',
        'ponto_encontro': 'Colonial',
        'telefone': 5512988247074

    },

    'Alita Amancio': {

        'nome_itinerario': 'Alita Amancio',
        'ponto_encontro': 'V.Flores',
        'telefone': 5512996360192

    },

    "Lucas Roberto": {

        'nome_itinerario': 'Lucas Roberto',
        'ponto_encontro': 'V.Flores',
        'telefone': 5512988105636

    },

    "Bruno Aragão": {

        'nome_itinerario': 'Bruno Aragão',
        'ponto_encontro': 'V.Flores',
        'telefone': 5512981534113

    },

    'Felipe Augusto': {

        'nome_itinerario': 'Felipe Augusto',
        'ponto_encontro': 'JJ',
        'telefone': None

    },

    "Daniel": {

        'nome_itinerario': 'Daniel Lima',
        'ponto_encontro': 'JJ',
        'telefone': 5512997930190

    },

    "Paulo": {

        'nome_itinerario': 'Paulo Granthon',
        'ponto_encontro': 'Dep. Ponte Alta',
        'telefone': 5522981249249

    },

    'Kaue': {

        'nome_itinerario': 'Kaue',
        'ponto_encontro': 'Av.Ouro Fino',
        'telefone': None

    },

    "Felipe Sobral": {

        'nome_itinerario': 'Felipe Sobral',
        'ponto_encontro': 'Satélite',
        'telefone': 5511964034305

    },

    "Marcos Vinícius Malaquias": {

        'nome_itinerario': 'Marcos Santos',
        'ponto_encontro': 'CPO',
        'telefone': 5512982970446

    },

    "Theo da Rosa Smidt": {

        'nome_itinerario': 'Theo da Rosa',
        'ponto_encontro': 'CTA',
        'telefone': 5512991473027

    },

}


# Função para ler dados do arquivo CSV
def ler_dados_csv():

    data = datetime.now()

    # Diretório relativo onde deseja salvar seu arquivo
    base_path = pathlib.Path("Enquetes")

    # Criando o nome do arquivo
    file_name = f"votes_{data.strftime('%Y-%m-%d')}.csv"

    # Combinando caminho e nome do arquivo
    full_path = base_path / file_name

    # Certifique-se de que o diretório existe
    if not full_path.parent.exists():
        full_path.parent.mkdir(parents=True)

    # Carregando dataframe
    df = pd.read_csv(full_path, sep=',', encoding='UTF-8', on_bad_lines='skip', header=0, skiprows=1)

    return df


def tratamento_dos_dados(df) -> str:

    # Substituir NaN por uma string vazia
    df.fillna('', inplace=True)

    # Renomear colunas para seguir sempre o padrão
    colunas = df.columns.tolist()
    colunas[0] = 'PASSAGEIRO'
    colunas[1] = 'TELEFONE'
    colunas[2] = 'VOU'
    colunas[3] = 'NÃO VOU'
    colunas[4] = 'SÓ VOLTO'
    df.columns = colunas

    passageiros_votos = iterar_votos_ao_dict_passageiros(df)

    vai = []
    volta = []
    n_vai = []
    # Iterando para excluir da lista os passageiros que não vão
    for k, v in passageiros_votos.items():

        if v["resposta_n_vai"] != '':
            n_vai.append(k)

    for chave in n_vai:
        del passageiros_votos[chave]

    # Iterar sobre cada linha dos passageiros que vão, voltam ou não responderam para gerar o txt
    for k, v in passageiros_votos.items():
        passageiro = v["passageiro"]
        telefone = v["telefone"]
        ponto_encontro = v["ponto_encontro"]

        if v["resposta_volta"] == '':
            linha_txt = (f'- {passageiro} {f"({ponto_encontro}) " if ponto_encontro is not None else ""}'
                         f'=> *NÃO RESPONDEU*{f" @{telefone}" if telefone is not None else ""} \n')

            if v["resposta_vai"] != '':
                linha_txt = linha_txt.split('=>', maxsplit=1)[0] + "\n"

            vai.append(linha_txt)

        else:
            linha_txt = f'- {passageiro} {f"({ponto_encontro}) " if ponto_encontro != "" else ""} \n'

            volta.append(linha_txt)

    mensagem = (f'*_IRÃO HOJE {datetime.now().day}/{datetime.now().month}_*\n\n'
                f'*Placa da van:* DXB5B96\n\n'
                f'*VAI:* \n\n{"".join(vai)}')

    if len(volta) > 0:
        mensagem = mensagem + f'\n*SÓ VOLTA:* \n\n{"".join(volta)}'

    return mensagem


def iterar_votos_ao_dict_passageiros(df) -> Dict[str, Dict[str, str]]:

    itinerario: Dict[str, Dict[str, str]] = {}
    i = 0
    for k, v in passageiros.items():

        i += 1

        for index, row in df.iterrows():
            passageiro = row['PASSAGEIRO']
            telefone = row['TELEFONE']
            resposta_vai = row['VOU']
            resposta_volta = row['SÓ VOLTO']
            resposta_n_vai = row['NÃO VOU']

            dict_passageiro: Dict[str, str] = {}

            if k not in df['PASSAGEIRO'].values:

                passageiro = v['nome_itinerario']
                ponto_encontro = v['ponto_encontro']
                telefone = v['telefone']

                dict_passageiro = {
                    "passageiro": passageiro,
                    "telefone": telefone,
                    "ponto_encontro": ponto_encontro,
                    "resposta_vai": '',
                    "resposta_volta": '',
                    "resposta_n_vai": ''
                }

                itinerario[f'Passageiro_{i}'] = dict_passageiro

            elif passageiro == k:

                passageiro = v['nome_itinerario']
                ponto_encontro = v['ponto_encontro']

                if telefone != v['telefone']:
                    telefone = None

                dict_passageiro = {
                    "passageiro": passageiro,
                    "telefone": telefone,
                    "ponto_encontro": ponto_encontro,
                    "resposta_vai": resposta_vai,
                    "resposta_volta": resposta_volta,
                    "resposta_n_vai": resposta_n_vai
                }

                itinerario[f'Passageiro_{i}'] = dict_passageiro

    return itinerario
