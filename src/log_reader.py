import os
import re
from typing import List, Optional

from log_entry import LogEntry


def get_log_files(directory: str) -> List[str]:
    """
    Recursively get all files in the directory that could be considered log files.
    For simplicity, we consider all files ending with '.log' as log files.
    """
    log_files = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.lower().endswith(".log"):
                log_files.append(os.path.join(root, f))
    return log_files


def get_log_lines(log_file: str) -> List[str]:
    """
    Read all lines from the provided log file into a list.
    """
    all_lines = []
    with open(log_file, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line:  # ignore empty lines
                all_lines.append(line)
    return all_lines


def get_log_entries(log_lines: List[str], log_file: str) -> List[LogEntry]:
    """
    Process a list of log lines and return log entries.

    :param log_lines: List of log lines.
    :param log_file: The name of the log file.
    :return: List of LogEntry objects.
    """
    log_entries = []
    for line in log_lines:
        line = line.strip()
        if line:  # ignore empty lines
            timestamp = get_timestamp(line)
            log_entry = LogEntry(message=line)
            log_entry.add_file(log_file)  # Add the log file name
            if timestamp:
                log_entry.add_timestamp(timestamp)
            log_entries.append(log_entry)
    return log_entries


def get_timestamp(text: str) -> Optional[str]:
    """
    Return the first timestamp in the string if any exist, otherwise None.
    """
    timestamp_patterns = [
        r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z",  # ISO 8601 format
    ]

    first_timestamp = None
    for pattern in timestamp_patterns:
        match = re.search(pattern, text)
        if match and not first_timestamp:
            first_timestamp = match.group(0)
    return first_timestamp
