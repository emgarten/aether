import base64
import hashlib
import re
from collections import namedtuple

# reference to a log entry
LogEntryRef = namedtuple("LogEntryRef", ["file", "line", "timestamp"])

# Parsed file name
PodInfo = namedtuple("PodInfo", ["namespace", "component", "pod", "container"])

POD_INFO_PATTERN = re.compile(r"^(?:(?P<namespace>[^/]+)/)?" r"(?:(?P<component>[^/]+)/)?" r"pod\.(?P<pod>[^.]+?)(?:\.(?P<container>[^.]+))?\.log$")


# LogEntry class is used for merging log lines together
class LogEntry:
    __slots__ = ["references", "message"]

    def __init__(self, message: str) -> None:
        self.message = message
        self.references: set[LogEntryRef] = set()

    def add_ref(self, ref: LogEntryRef) -> None:
        """Add a reference to the line in the log file."""
        self.references.add(ref)

    def get_id(self) -> str:
        """Return a unique identifier for the log entry."""
        return get_hash(self.message)

    def merge(self, other: "LogEntry") -> None:
        """Merge another log entry into this one."""
        for ref in other.references:
            self.add_ref(ref)


def get_hash(input_string: str, length: int = 6) -> str:
    full_hash = hashlib.sha256(input_string.encode()).digest()
    return base64.urlsafe_b64encode(full_hash).decode()[:length]


# File path -> PodInfo
def parse_pod_info(file_path: str) -> PodInfo:
    match = POD_INFO_PATTERN.match(file_path)
    if match:
        return PodInfo(
            namespace=match.group("namespace"),
            component=match.group("component"),
            pod=match.group("pod"),
            container=match.group("container"),
        )
    return PodInfo(None, None, None, None)
