import os

from typing import Dict, List, Union, Optional
from pathlib import Path

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from .utils import project_paths, Secrets

class GoogleSheet:
    def __init__(self, spreadsheet_id: str = None):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.token = project_paths.get_secrets() / 'token.json'
        self.credentials = project_paths.get_secrets() / 'credentials.json'
        self.spreadsheet_id = spreadsheet_id

        if not self.credentials.exists():
            print("No existe el archivo 'secrets/credentials.json'")
            credentials_path = self.input_credentials_filepath()
            Secrets().add_secret(credentials_path)

        def input_credentials_filepath(self) -> Optional[Path]:
            try:
                return Path(input("Escribe la ubicacion del archivo (/home/usuario/Download/nombre_del_archivo.json): "))
            except Exception as error:
                print(f"Error al ingresar la ubicacion del archivo de credenciales: {error}")
                return None

    def get_sheet_services(self):
        creds = None
        if self.have_token():
            creds = Credentials.from_authorized_user_file(self.token, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(self.token, 'w') as token:
                token.write(creds.to_json())

        return build('sheets', 'v4', credentials=creds)

    def format_column(self, spreadsheet_id, range_, format_type):
        service = self.get_sheet_services()
        
        sheet_metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheets = sheet_metadata.get('sheets', [])
        sheet_id = sheets[0]['properties']['sheetId']

        if format_type == "date":
            format_request = {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startColumnIndex": 0,
                        "endColumnIndex": 1,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                                "type": "DATE",
                                "pattern": "yyyy-mm-dd"
                            }
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat"
                }
            }
        elif format_type == "currency":
            format_request = {
                "repeatCell": {
                    "range": {
                        "sheetId": sheet_id,
                        "startColumnIndex": 1,
                        "endColumnIndex": 2,
                    },
                    "cell": {
                        "userEnteredFormat": {
                            "numberFormat": {
                                "type": "CURRENCY",
                                "pattern": "#,##0.00"
                            }
                        }
                    },
                    "fields": "userEnteredFormat.numberFormat"
                }
            }
        else:
            print("Tipo de formato no soportado")
            return

        batch_update_request = {
            "requests": [format_request]
        }
        try:
            response = service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, 
                body=batch_update_request
            ).execute()
            print(f"Formato actualizado correctamente: {response}")
        except Exception as error:
            print(f"Error al actualizar el formato: {error}")


    def upload_to_sheets(self, fieldnames: List[str], data_dicts: List[Dict[str, Union[str, int]]]):
        if not self.spreadsheet_id:
            print("No se ha creado un spreadsheet. No se pueden cargar los datos.")
            return

        service = self.get_sheet_services()

        values = [fieldnames]  # Encabezados
        for row in data_dicts:
            values.append([row[field] for field in fieldnames])

        try:
            sheet_metadata = service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()

            sheets = sheet_metadata.get('sheets', [])
            sheet_name = sheets[0]['properties']['title']
            range_ = f'{sheet_name}!A1'

            body = {
                'values': values
            }

            request = service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_,
                valueInputOption="RAW",
                body=body
            )
            response = request.execute()
            print(f"Datos subidos correctamente: {response}")

            self.format_column(self.spreadsheet_id, range_, "date")
            self.format_column(self.spreadsheet_id, range_, "currency")
        except Exception as error:
            print(f"Error al cargar los datos: {error}")
