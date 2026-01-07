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

    def add_secret(self, filepath: Path):
        try:
            with filepath.open("r", encoding="utf-8") as source_file:
                data = json.load(source_file)

            destination = self.SECRETS_PATH / "credentials.json"

            with destination.open("w", encoding="utf-8") as newfile:
                json.dump(data, newfile, indent=2, ensure_ascii=False)

            print(f"Archivo secreto agegado exitosamente: {destination}")
        except json.JSONDecodeError as error:
            print(f"Error: El archivo no es un JSON válido - {error}")
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {filepath}")
        except Exception as error:
            print(f"Error al intentar agregar un archivo secreto: {error}")

    def remove_secret(self, filepath: PosixPath):
        try:
            file = self.SECRETS_PATH / filepath
            file.unlink()
        except Exception as error:
            print(f"Error al intentar eliminar un archivo secreto: {error}")
