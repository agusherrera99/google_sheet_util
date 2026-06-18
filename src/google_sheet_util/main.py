import json
import os

from typing import Dict, List, Union, Optional
from pathlib import Path

from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from .utils import Secret

class GoogleSheet:
    def __init__(self, credentials: Optional[Path] = None, token: Optional[Path] = None, spreadsheet_id: Optional[str] = None):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.secret = Secret()
        self.token = token or self.secret.get_token()
        self.credentials = credentials or self.secret.get_credentials()
        self.spreadsheet_id = spreadsheet_id

        if self.credentials is None or not self.credentials.exists():
            print("No existe el archivo 'secrets/credentials.json'")

            credentials_path = self.input_credentials_filepath()
            self.secret.add_secret(credentials_path)

    def input_credentials_filepath(self) -> Optional[Path]:
        try:
            return Path(input("Escribe la ubicacion del archivo (/home/usuario/Download/nombre_del_archivo.json): "))
        except Exception as error:
            print(f"Error al ingresar la ubicacion del archivo de credenciales: {error}")
            return None

def format_column(self, sheet_id, format_type, start_col, end_col):
        """Genera la estructura del request de formato sin ejecutarla."""
        patterns = {
            "date": {"type": "DATE", "pattern": "yyyy-mm-dd"},
            "currency": {"type": "CURRENCY", "pattern": "#,##0.00"},
            "number": {"type": "NUMBER", "pattern": "#,##0.00"}
        }

        if format_type not in patterns:
            return None

        return {
            "repeatCell": {
                "range": {
                    "sheetId": sheet_id,
                    "startColumnIndex": start_col,
                    "endColumnIndex": end_col,
                },
                "cell": {
                    "userEnteredFormat": {
                        "numberFormat": patterns[format_type]
                    }
                },
                "fields": "userEnteredFormat.numberFormat"
            }
        }


    def upload_to_sheets(self, fieldnames: List[str], data_dicts: List[Dict[str, Union[str, int]]], column_formats: Dict[str, str], range_value: str):
        if not self.spreadsheet_id:
            print("No se ha creado un spreadsheet. No se pueden cargar los datos.")
            return

        service = self._get_sheet_services()

        values = [fieldnames]
        for row in data_dicts:
            values.append([row[field] for field in fieldnames])

        try:
            sheet_metadata = service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()

            sheets = sheet_metadata.get('sheets', [])
            sheet_name = sheets[0]['properties']['title']
            sheet_id = sheets[0]['properties']['sheetId']
            full_range = f'{sheet_name}!{range_value}'

            body = {
                'values': values
            }

            request = service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=full_range,
                valueInputOption="RAW",
                body=body
            )
            response = request.execute()

            requests_batch = []
            for index, field in enumerate(fieldnames):
                format_type = column_formats.get(field)

                if format_type in ["currency", "date", "number"]:
                    req = self.format_column(sheet_id, format_type, index, index + 1)
                    if req:
                        requests_batch.append(req)

            if requests_batch:
                batch_update_request = {
                    "requests": requests_batch
                }
                batch_response = service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id, 
                    body=batch_update_request
                ).execute()
                print(f"Formatos actualizados correctamente: {batch_response}")

            print(f"Datos subidos correctamente: {response}")
        except Exception as error:
            print(f"Error al cargar los datos: {error}")
            raise

    def read_sheet(self, sheet_name: str, range_value: str):
        service = self._get_sheet_services()
        rows = []
        range_ = f"{sheet_name}!{range_value}"

        try:
            request = service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_
            )
            response = request.execute()

            values = response.get("values", [])
            if not values:
                prit("No data found.")
                return

            for row in values:
                rows.append(row)
            return rows
        except Exception as error:
            print(f"Error al leer los datos: {error}")
            raise

    def _get_sheet_services(self):
        creds = None
        try:
            with open(self.credentials, 'r') as file:
                creds_data = json.load(file)

            if creds_data.get('type') == 'service_account':
                creds = service_account.Credentials.from_service_account_info(
                    creds_data, scopes=self.SCOPES
                )
                return build('sheets', 'v4', credentials=creds)

            if self.token and self.token.exists():
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

        except Exception as e:
            print(f"Error crítico al obtener servicios de Google Sheets: {e}")
            raise
