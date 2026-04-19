from abc import ABC, abstractmethod
from pathlib import Path


class StorageBackend(ABC):
    @abstractmethod
    def save(self, path: str, content: bytes) -> None:
        pass

    @abstractmethod
    def load(self, path: str) -> bytes:
        pass

    @abstractmethod
    def delete(self, path: str) -> None:
        pass


class LocalStorage(StorageBackend):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, path: str, content: bytes) -> None:
        target = self.base_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def load(self, path: str) -> bytes:
        return (self.base_path / path).read_bytes()

    def delete(self, path: str) -> None:
        (self.base_path / path).unlink(missing_ok=True)
