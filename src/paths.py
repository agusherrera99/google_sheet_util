from pathlib import Path

class ProjectPaths:
    def __init__(self):
        self.ROOT_PATH = Path(__file__).resolve().parent.parent
        self.SRC_PATH = self.ROOT_PATH / "src"
        self.SECRETS_PATH = self.ROOT_PATH / "secrets"

    def get_root(self):
        return self.ROOT_PATH

    def get_src(self):
        return self.SRC_PATH

    def get_secrets(self):
        return self.SECRETS_PATH

project_paths = ProjectPaths()
