import logging
import pathlib
from datetime import datetime
import gerar_itinerario as gerar


# Setup Logging Debug
logging.addLevelName(25, "C_INFO-DEV")
logging.addLevelName(23, "C_INFO-PROD")
logging.addLevelName(21, "C_DEBUG")
logging.basicConfig(level=21)


if __name__ == "__main__":

    # Ler os dados do arquivo CSV
    df = gerar.ler_dados_csv()

    # Tratar os dados e transformar em string para envio da mensagem
    mensagem = gerar.tratamento_dos_dados(df)

    # >>> Gerar a mensagem para o grupo do WhatsApp, gerando arquivo local e printando ele também
    data = datetime.now()

    # Diretório relativo onde deseja salvar seu arquivo
    base_path = pathlib.Path("Itinerários")

    # Criando o nome do arquivo
    file_name = f"itinerario_{data.strftime('%Y-%m-%d')}.txt"

    # Combinando caminho e nome do arquivo
    full_path = base_path / file_name

    # Certifique-se de que o diretório existe
    if not full_path.parent.exists():
        full_path.parent.mkdir(parents=True)

    # Salvando o arquivo
    with open(full_path, 'w') as arquivo:
        arquivo.write(mensagem)

    print(mensagem)
