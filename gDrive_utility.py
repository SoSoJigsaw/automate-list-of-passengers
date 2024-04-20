from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.http import MediaIoBaseDownload
import io, os, logging


SCOPES = ['https://www.googleapis.com/auth/drive']


def ensureDirExists(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


# Function to authenticate and create the Drive service
def create_drive_service():
    creds = None

    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=38666)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)


def getFileDict_fromFolder_recursively(folder_id, service, fileDict=None):
    """\
    Recursively gets ALL files from this folder on.
    """
    if fileDict is None:
        fileDict = {}
    query = f"'{folder_id}' in parents and trashed = false"
    response = service.files().list(q=query, spaces='drive', fields='nextPageToken, files(id, name, mimeType)',
                                    pageToken=None).execute()
    for file in response.get('files', []):
        if file.get('mimeType') == 'application/vnd.google-apps.folder':
            getFileDict_fromFolder_recursively(file.get('id'), service, fileDict)
        else:
            fileDict[file.get('name')] = (file.get('id'), file.get('mimeType'))
    return fileDict


def getFoldersDict(target_folder_name=None):
    """\
    Returns a dict[str, str] of all folders in the Google Drive.
    dict structure is:
        Key is folder name
        Value is folder ID
    """
    service = create_drive_service()

    # Query to search for folders
    query = "mimeType='application/vnd.google-apps.folder' and trashed = false"

    # Optionally focus on a specific folder
    if target_folder_name:
        query += f" and name = '{target_folder_name}'"

    # Call the Drive v3 API
    response = service.files().list(q=query,
                                    spaces='drive',
                                    fields='nextPageToken, files(id, name)',
                                    pageToken=None).execute()

    folderDict = {}
    for folder in response.get('files', []):
        logging.log(21, f"gDrive | Folder ID: {folder.get('id')} Name: {folder.get('name')}")

        folderDict[folder.get('name')] = folder.get('id')

    return folderDict


def download_or_export_file(file_id, file_name, mime_type, path="lista_passageiros"):
    """\
    Se o download_file() falhar, provavelmente é um arquivo nativo do Google.
    Esta função trata Docs, Sheets, Presentation e Drawing.
    """
    # Pular pastas/diretórios
    if mime_type == 'application/vnd.google-apps.folder':
        logging.log(21, f"Pasta ignorada: {file_name} ({file_id})")
        return

    ensureDirExists(path)
    service = create_drive_service()

    # Define tipos de exportação MIME para diferentes arquivos do Google Apps
    google_mime_types = {
        'application/vnd.google-apps.spreadsheet': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.google-apps.document': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.google-apps.presentation': 'application/pdf',
        'application/vnd.google-apps.drawing': 'image/jpeg'
    }

    export_mime_type = google_mime_types.get(mime_type, None)

    data_atual = datetime.now()

    # Decide o tipo de exportação, com base nas informações de tipo MIME do Google
    if export_mime_type:
        # Se for um arquivo do Google Sheets, exporte como CSV
        if export_mime_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
            logging.log(21, "gDrive: Arquivo do Google Sheets detectado...")
            request = service.files().export_media(fileId=file_id, mimeType='text/csv')
            file_name = f"{os.path.splitext(file_name)[0]}_{data_atual.strftime('%Y-%m-%d')}.csv"
    else:
        # Para todos os outros arquivos, prossiga com o download normal do arquivo
        logging.warning(
            f"gDrive: Arquivo não especial detectado ou tentativa de baixar uma pasta. {mime_type=}\n{file_name=}\n{file_id=}"
        )
        request = service.files().get_media(fileId=file_id)

    # Baixando o arquivo
    fh = io.FileIO(os.path.join(path, file_name), 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.close()

    logging.log(23, f"gDrive | Baixado/Exportado '{file_name}' com sucesso.")


def empty_folder(folder_id):
    """Esvazia um diretório do Google Drive."""
    service = create_drive_service()

    # Obter a lista de todos os arquivos no diretório
    query = f"'{folder_id}' in parents and trashed = false"
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)', pageToken=None).execute()
    files = response.get('files', [])

    # Excluir cada arquivo no diretório
    for file in files:
        try:
            service.files().delete(fileId=file['id']).execute()
            logging.info(f"Arquivo '{file['name']}' excluído com sucesso.")
        except Exception as e:
            logging.error(f"Falha ao excluir o arquivo '{file['name']}': {str(e)}")


def get_folder_id(folder_name):
    """Retorna o ID do diretório com o nome especificado."""
    service = create_drive_service()

    # Query para buscar o diretório pelo nome
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])

    # Verificar se o diretório foi encontrado
    if files:
        folder_id = files[0]['id']
        logging.info(f"ID do diretório '{folder_name}': {folder_id}")
        return folder_id
    else:
        logging.error(f"Diretório '{folder_name}' não encontrado.")
        return None


def empty_folder_by_name(folder_name):
    """Esvazia um diretório do Google Drive pelo nome."""
    folder_id = get_folder_id(folder_name)
    if folder_id:
        empty_folder(folder_id)


def move_sheet_to_folder(sheet_file_id, source_folder_id, target_folder_id):
    """Move um arquivo do Google Sheets de uma pasta para outra, mantendo uma cópia."""
    service = create_drive_service()

    # Obter o nome do arquivo original
    file_metadata = service.files().get(fileId=sheet_file_id, fields='name, parents').execute()
    file_name = file_metadata['name']
    current_parents = file_metadata.get('parents', [])

    # Copiar o arquivo para a pasta de destino
    copied_file_metadata = {'name': file_name, 'parents': [target_folder_id]}
    copied_file = service.files().copy(fileId=sheet_file_id, body=copied_file_metadata).execute()
    logging.info(f"Arquivo copiado para a pasta de destino: '{file_name}'")

    # Remover o arquivo da pasta de origem
    if source_folder_id in current_parents:
        current_parents.remove(source_folder_id)
        updated_file_metadata = {'name': file_name, 'parents': current_parents}
        updated_file = service.files().update(fileId=sheet_file_id, body=updated_file_metadata).execute()
        logging.info(f"Arquivo removido da pasta de origem: '{file_name}'")
    else:
        logging.warning(f"Arquivo não encontrado na pasta de origem: '{file_name}'")


def get_document_id(document_name, parent_folder_id):
    """Retorna o ID do documento com o nome especificado dentro de um diretório."""
    service = create_drive_service()

    # Query para buscar o documento pelo nome e dentro do diretório especificado
    query = f"name='{document_name}' and '{parent_folder_id}' in parents and mimeType!='application/vnd.google-apps.folder' and trashed=false"
    response = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    files = response.get('files', [])

    # Verificar se o documento foi encontrado
    if files:
        document_id = files[0]['id']
        logging.info(f"ID do documento '{document_name}' no diretório '{parent_folder_id}': {document_id}")
        return document_id
    else:
        logging.error(f"Documento '{document_name}' não encontrado no diretório '{parent_folder_id}'.")
        return None
