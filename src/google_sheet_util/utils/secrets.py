import json

from pathlib import PosixPath

from .paths import project_paths

class Secret:
    def __init__(self):
        self.SECRETS_PATH = project_paths.get_secrets()

    def add_secret(self, filepath: PosixPath):
        try:
            with filepath.open("w", encoding="utf-8") as newfile:
                newfile.write(result)
        except Exception as error:
            print(f"Error al intentar agregar un archivo secreto: {error}")

    def remove_secret(self, filepath: PosixPath):
        try:
            file = self.SECRETS_PATH / filepath
            file.unlink()
        except Exception as error:
            print(f"Error al intentar eliminar un archivo secreto: {error}")
