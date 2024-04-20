import logging
from datetime import datetime
import time
import dotenv
import os
import send_message as sm
import gDrive_utility
import gDrive_utility as gDrive


# Load environment variables
dotenv.load_dotenv()

# Setup Logging Debug
logging.addLevelName(25, "C_INFO-DEV")
logging.addLevelName(23, "C_INFO-PROD")
logging.addLevelName(21, "C_DEBUG")
logging.basicConfig(level=21)


if __name__ == "__main__":

    # Definir o horário de envio da mensagem
    horario_envio = datetime(2024, 1, 1, 17, 0, 0)

    # Loop infinito para verificar o horário e enviar a mensagem
    while True:

        agora = datetime.now().time()

        if agora.hour == horario_envio.hour and agora.minute == horario_envio.minute:

            # Extraindo o sheet atualizado do Google Drive
            file_path = os.path.join("lista_passageiros", "lista_passageiros.txt")
            with open(file_path, 'w') as file:
                file.write("empty state\n")

            # We'll only get files from this folder
            lista_passageiros_id = gDrive.getFoldersDict(target_folder_name='lista_passageiros')

            # Recursively get ALL FILES from it
            if lista_passageiros_id and os.getenv('SHOULD_GDRIVE', "true").lower() == "true":
                service = gDrive.create_drive_service()

                logging.log(21, f"Starting Google Drive utility program...")
                for _folderName, folderID in lista_passageiros_id.items():

                    dictFiles = gDrive.getFileDict_fromFolder_recursively(folderID, service)

                    logging.log(21, f"\n\ngDrive: {dictFiles=}\n")

                    for fileName, fileInfo in dictFiles.items():
                        fileID, mimeType = fileInfo
                        try:
                            gDrive.download_or_export_file(
                                file_id=fileID,
                                file_name=fileName,
                                mime_type=mimeType,
                                path=os.path.join("lista_passageiros")
                            )
                        except Exception as e:
                            logging.warning(f"gDrive: FAILED to download file: {e}")

                    try:
                        gDrive.empty_folder_by_name("lista_passageiros")
                    except Exception as e:
                        logging.warning(f"gDrive: FAILED to delete file: {e}")

                    try:
                        gDrive.move_sheet_to_folder(
                            sheet_file_id=gDrive.get_document_id("lista_passageiros", gDrive_utility.get_folder_id(
                                "modelo_lista_passageiros")),
                            source_folder_id=gDrive.get_folder_id("modelo_lista_passageiros"),
                            target_folder_id=gDrive.get_folder_id("lista_passageiros")
                        )
                    except Exception as e:
                        logging.warning(f"gDrive: FAILED to move file: {e}")

            # Now that we're done processing, communicate we're done.
            with open(file_path, 'w') as file:
                print("service_gDrive: ok")
                file.write("service_gDrive: ok\n")

            time.sleep(15)

            # Ler os dados do arquivo CSV
            df = sm.ler_dados_csv()

            # Tratar os dados e transformar em string para envio da mensagem
            mensagem = sm.tratamento_dos_dados(df)

            # Enviar a mensagem para o grupo do WhatsApp
            sm.enviar_mensagem_grupo_whatsapp(grupo="VAN FATEC NOTURNO", mensagem=mensagem)

            break

        else:
            print(f'{datetime.now().time()} agora. Ainda não está no horário de envio marcado: {horario_envio.time()}. '
                  f'Aguardar mais 1 minuto para nova verificação.')

            # Aguardar 1 minuto antes de verificar novamente o horário
            time.sleep(60)
