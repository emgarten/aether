class LogEntry:
    def __init__(self, message: str):
        self.files = set()
        self.timestamps = set()
        self.message = message

    def add_file(self, file: str):
        """Add a unique file to the log entry."""
        self.files.add(file)

    def add_timestamp(self, timestamp: str):
        """Add a unique timestamp to the log entry."""
        self.timestamps.add(timestamp)

    def merge(self, *entries: "LogEntry"):
        """Merge files and timestamps from other LogEntry instances into this instance."""
        for entry in entries:
            self.files.update(entry.files)
            self.timestamps.update(entry.timestamps)

    def to_dict(self):
        """Convert the LogEntry to a dictionary for JSON serialization."""
        return {
            "files": list(self.files),
            "timestamps": list(self.timestamps),
            "message": self.message
        }