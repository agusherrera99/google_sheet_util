from pathlib import Path

class ProjectPaths:
    def __init__(self):
        self.ROOT_PATH = Path(__file__).resolve().parent.parent
        self.SECRETS_PATH = self.ROOT_PATH / "secrets"

    def get_secrets(self):
        return self.SECRETS_PATH

project_paths = ProjectPaths()
