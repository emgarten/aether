import base64
import hashlib
from collections import namedtuple
from datetime import datetime

# reference to a log entry
LogEntryRef = namedtuple("LogEntryRef", ["file", "line", "timestamp"])


# LogEntry class is used for merging log lines together
class LogEntry:
    __slots__ = ["references", "message"]

    def __init__(self, message: str, file: str, line: int, timestamp: datetime) -> None:
        self.message = message
        self.references = set()
        self.add_ref(LogEntryRef(file, line, timestamp))

    def add_ref(self, ref: LogEntryRef) -> None:
        """Add a reference to the line in the log file."""
        self.references.add(ref)

    def get_id(self) -> str:
        """Return a unique identifier for the log entry."""
        return get_hash(self.message)

    def merge(self, other: any) -> None:
        """Merge another log entry into this one."""
        for ref in other.references:
            self.add_ref(ref)


def get_hash(input_string: str, length: int = 6) -> str:
    full_hash = hashlib.sha256(input_string.encode()).digest()
    return base64.urlsafe_b64encode(full_hash).decode()[:length]
