import zipfile
from pathlib import Path


class FileSystem:
    def __init__(self, path):
        self.path = Path(path)
        if self.path.is_file() and self.path.suffix == ".zip":
            self.zip_mode = True
            self.zip_file = zipfile.ZipFile(self.path, "r")
        elif self.path.is_dir():
            self.zip_mode = False
        else:
            raise ValueError("Path must be either a directory or a ZIP file.")

    def list_files(self):
        if self.zip_mode:
            return self.zip_file.namelist()
        else:
            return [str(file.relative_to(self.path)) for file in self.path.rglob("*") if file.is_file()]

    def read_file(self, file_name):
        if self.zip_mode:
            with self.zip_file.open(file_name) as f:
                return f.read()
        else:
            with open(self.path / file_name, "rb") as f:
                return f.read()

    def __del__(self):
        if self.zip_mode:
            self.zip_file.close()
