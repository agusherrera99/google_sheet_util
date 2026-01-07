import json

from pathlib import PosixPath

from .paths import project_paths

class Secret:
    def __init__(self):
        self.SECRETS_PATH = project_paths.get_secrets()

    def read_json(self, filepath: PosixPath):
        try:
            with open(filepath, "r") as file:
                data = json.load(file)
                return data
        except Exception as error:
            print(f"Error al intentar leer archivo json: {error}")

    def add_secret(self, filepath: PosixPath):
        try:
            secret = self.read_json(filepath)
            with secret.open("w", encoding="utf-8") as newfile:
                newfile.write(result)
        except Exception as error:
            print(f"Error al intentar agregar un archivo secreto: {error}")

    def remove_secret(self, filepath: PosixPath):
        try:
            file = self.SECRETS_PATH / filepath
            file.unlink()
        except Exception as error:
            print(f"Error al intentar eliminar un archivo secreto: {error}")
