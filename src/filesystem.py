import zipfile
from pathlib import Path
from typing import List, Union


class FileSystem:
    def __init__(self, path: Union[str, Path]) -> None:
        self.path = Path(path)
        if self.path.is_file() and self.path.suffix == ".zip":
            self.zip_mode = True
            self.zip_file = zipfile.ZipFile(self.path, "r")
        elif self.path.is_dir():
            self.zip_mode = False
        else:
            raise ValueError("Path must be either a directory or a ZIP file.")

    def list_files(self) -> List[str]:
        if self.zip_mode:
            return self.zip_file.namelist()
        else:
            return [str(file.relative_to(self.path)) for file in self.path.rglob("*") if file.is_file()]

    def read_file(self, file_name: str) -> List[str]:
        """
        Return the contents of `file_name` as a list of strings (one for each line).
        Trailing slashes are removed to ensure correct handling of directories vs. files.
        """
        file_name = file_name.rstrip("/\\")  # Remove any trailing slashes

        if self.zip_mode:
            with self.zip_file.open(file_name, "r") as f:
                return f.read().decode("utf-8").splitlines()
        else:
            with open(self.path / file_name, "r", encoding="utf-8") as f:
                return f.read().splitlines()

    def __del__(self) -> None:
        if self.zip_mode:
            self.zip_file.close()
