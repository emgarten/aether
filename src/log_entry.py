import base64
import hashlib


class LogEntry:
    def __init__(self, message: str) -> None:
        self.files = set()
        self.timestamps = set()
        self.message = message
        self.id = get_hash(message)

    def add_file(self, file: str) -> None:
        """Add a unique file to the log entry."""
        self.files.add(file)

    def add_timestamp(self, timestamp: str) -> None:
        """Add a unique timestamp to the log entry."""
        self.timestamps.add(timestamp)


def get_hash(input_string: str, length: int = 6) -> str:
    full_hash = hashlib.sha256(input_string.encode()).digest()
    return base64.urlsafe_b64encode(full_hash).decode()[:length]
