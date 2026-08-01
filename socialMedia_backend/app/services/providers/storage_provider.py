import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO


class StorageProvider(ABC):
    @abstractmethod
    def save_file(self, file_obj: BinaryIO, filename: str) -> str:
        """Saves a file and returns its access path/URL."""
        
    @abstractmethod
    def delete_file(self, filepath: str) -> bool:
        """Deletes a file."""

class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: str = "uploads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
    def save_file(self, file_obj: BinaryIO, filename: str) -> str:
        dest_path = self.base_dir / filename
        with open(dest_path, "wb") as buffer:
            shutil.copyfileobj(file_obj, buffer)
        return str(dest_path)
        
    def delete_file(self, filepath: str) -> bool:
        path = Path(filepath)
        if path.exists():
            os.remove(path)
            return True
        return False

# Future: SupabaseStorageProvider or S3StorageProvider could implement this interface.
