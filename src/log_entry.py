class LogEntry:
    def __init__(self, message: str) -> None:
        self.files = set()
        self.timestamps = set()
        self.message = message

    def add_file(self, file: str) -> None:
        """Add a unique file to the log entry."""
        self.files.add(file)

    def add_timestamp(self, timestamp: str) -> None:
        """Add a unique timestamp to the log entry."""
        self.timestamps.add(timestamp)

    def to_dict(self) -> dict:
        """Convert the LogEntry to a dictionary for JSON serialization."""
        return {
            "files": list(self.files),
            "timestamps": list(self.timestamps),
            "message": self.message,
        }
