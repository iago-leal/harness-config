import os
from typing import List
from src.core.ports.fs import FileSystemPort

class LocalFileSystemAdapter(FileSystemPort):
    def read_file(self, path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, path: str, content: str) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

    def write_file_atomic(self, path: str, content: str) -> None:
        # Cria arquivo temporário .tmp no mesmo diretório
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
            
        filename = os.path.basename(path)
        tmp_path = os.path.join(directory, f".{filename}.tmp")
        
        try:
            with open(tmp_path, 'w', encoding='utf-8') as f:
                f.write(content)
            # Substituição atômica no SO
            os.replace(tmp_path, path)
        except Exception as e:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise e

    def exists(self, path: str) -> bool:
        return os.path.exists(path)

    def list_dir(self, path: str) -> List[str]:
        return os.listdir(path)

    def makedirs(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)

    def remove(self, path: str) -> None:
        if os.path.exists(path):
            os.remove(path)

    def is_dir(self, path: str) -> bool:
        return os.path.isdir(path)

