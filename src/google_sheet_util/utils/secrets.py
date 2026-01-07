import json

from pathlib import Path, PosixPath

class Secret:
    def __init__(self, base_path=None):
        if base_path is None:
            base_path = Path.cwd()
        else:
            base_path = Path(base_path)

        self.SECRETS_PATH = base_path / "secrets"
        self.SECRETS_PATH.mkdir(parents=True, exist_ok=True)

    def get_content(self, filepath: Path):
        try:
            with filepath.open("r", encoding="utf-8") as source_file:
                content = source_file.read()
            return content
        except Exception as error:
            print(f"Error al intentar obtener el contenido del archivo: {error}")

    def add_secret(self, filepath: Path):
        try:
            destination = self.SECRETS_PATH / "credentials.json"
            with destination.open("w", encoding="utf-8") as newfile:
                newfile.write(self.get_content(filepath))

            print(f"Archivo secreto agegado exitosamente: {destination}")
        except Exception as error:
            print(f"Error al intentar agregar un archivo secreto: {error}")

    def remove_secret(self, filepath: PosixPath):
        try:
            file = self.SECRETS_PATH / filepath
            file.unlink()
        except Exception as error:
            print(f"Error al intentar eliminar un archivo secreto: {error}")
