import re
from datetime import datetime
from typing import List, Optional

from filesystem import FileSystem
from log_entry import LogEntry, LogEntryRef
from rapidfuzz import fuzz


# Entry point for the log clustering process
class LogClusterer:

    def __init__(self, threshold: float):
        self.threshold = threshold

    def cluster(self, entries: List[LogEntry]) -> List[LogEntry]:
        return fuzzy_match_entries(entries, self.threshold)

    def cluster_files(self, fs: FileSystem, namespace: str) -> List[LogEntry]:
        cross_file_entries = []

        # Cluster within each file
        for file in fs.list_files():
            if allow_log_path(file, namespace):
                log_lines = fs.read_file(file)
                file_entries = get_log_entries(log_lines, file)
                file_clustered_entries = self.cluster(file_entries)
                cross_file_entries.extend(file_clustered_entries)

        # Cluster across all files
        return self.cluster(cross_file_entries)


def allow_log_path(path: str, namespace: str) -> bool:
    lower_path = path.lower()
    if lower_path.startswith(f"{namespace.lower()}/") and lower_path.endswith(".log"):
        return True
    return False


def get_log_entries(log_lines: List[str], log_file: str) -> List[LogEntry]:
    """
    Process a list of log lines and return log entries.

    :param log_lines: List of log lines.
    :param log_file: The name of the log file.
    :return: List of LogEntry objects.
    """
    log_entries = []
    for i in range(0, len(log_lines)):
        line = log_lines[i].strip()
        if line:  # ignore empty lines
            timestamp = get_timestamp(line)
            log_entry = LogEntry(message=line)
            log_entry.add_ref(LogEntryRef(log_file, i, timestamp))
            log_entries.append(log_entry)
    return log_entries


def get_timestamp(text: str) -> Optional[datetime]:
    """
    Return the first timestamp in the string if any exist, otherwise None.
    """
    timestamp_patterns = [
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z",  # ISO 8601 format
    ]

    first_timestamp = None
    for pattern in timestamp_patterns:
        match = re.search(pattern, text)
        if match:
            first_timestamp = match.group(0)
            try:
                return datetime.fromisoformat(first_timestamp)
            except:  # noqa: E722
                # Ignore
                pass

    return None


def fuzzy_match_entries(entries: List[LogEntry], threshold: float) -> List[LogEntry]:
    """
    Cluster the entries based on the similarity of their message fields.

    This uses a simple greedy approach:
      - Initialize an empty list of clusters.
      - For each entry:
        * Compare its message with representative messages of existing clusters.
        * If it matches a cluster's representative message with similarity >= threshold,
          add it to that cluster.
        * Otherwise, create a new cluster.

    Note: This is O(N^2) in worst case and may be slow for very large entries.
    For efficiency, consider using a more advanced technique or indexing.
    """
    clusters: List[LogEntry] = []
    for entry in entries:
        matched_cluster = False
        for cluster in clusters:
            # Compare against the cluster's representative message
            similarity = fuzz.ratio(entry.message, cluster.message)
            if similarity >= threshold:
                # Add to this cluster
                cluster.merge(entry)
                matched_cluster = True
                break
        if not matched_cluster:
            # Create a new cluster
            clusters.append(entry)

    return clusters
