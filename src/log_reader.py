import logging
import os
import re
import zipfile
from typing import List, Optional

from cluster import fuzzy_match_entries
from log_entry import LogEntry


def allow_log_path(path: str) -> bool:
    if "azure-iot-operations" in path.lower():
        return True


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


def get_folder_logs(path: str, fuzz_threshold: float) -> list:
    log_files = get_log_files(path)
    rep_lines = []
    # logging.debug("Log files found:", log_files)

    for log_file in log_files:
        # Limit to azure-iot-operations logs
        if allow_log_path(log_file):
            # Read all lines from the log file
            log_lines = get_log_lines(log_file)
            log_entries = get_log_entries(log_lines, log_file)

            # Cluster logs with rapidfuzz within a log file
            merged_log_entries = fuzzy_match_entries(log_entries, fuzz_threshold)
            for i, cluster in enumerate(merged_log_entries):
                rep_lines.append(cluster)

            logging.debug(f"Log file: {log_file} lines: {len(log_entries)} -> {len(merged_log_entries)}")

    # Merge log entries across all log files
    merged_rep_lines = fuzzy_match_entries(rep_lines, fuzz_threshold)
    logging.debug(f"Total unique log entries: {len(merged_rep_lines)}")
    return merged_rep_lines


def get_zip_logs(zip_path: str, fuzz_threshold: float) -> list:
    """
    Process log files within a zip archive and return clustered log entries.

    :param zip_path: Path to the zip file containing log files.
    :param fuzz_threshold: Threshold for fuzzy matching log entries.
    :return: List of clustered log entries.
    """
    rep_lines = []
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        # Extract all .log files from the zip archive
        for file_info in zip_ref.infolist():
            if file_info.filename.lower().endswith(".log"):
                # Limit to azure-iot-operations logs
                if allow_log_path(file_info.filename):
                    with zip_ref.open(file_info) as log_file:
                        logging.debug(f"Processing log file: {file_info.filename}")
                        log_lines = get_log_lines_from_file(log_file)
                        log_entries = get_log_entries(log_lines, file_info.filename)

                        merged_log_entries = fuzzy_match_entries(log_entries, fuzz_threshold)
                        for i, cluster in enumerate(merged_log_entries):
                            rep_lines.append(cluster)

    # Cluster logs with rapidfuzz within a log file
    merged_log_entries = fuzzy_match_entries(rep_lines, fuzz_threshold)
    logging.debug(f"Total unique log entries from zip: {len(merged_log_entries)}")
    return merged_log_entries


def get_log_lines_from_file(file) -> List[str]:
    """
    Read all lines from the provided file-like object into a list.
    """
    all_lines = []
    for line in file:
        line = line.decode("utf-8", errors="replace").strip()
        if line:  # ignore empty lines
            all_lines.append(line)
    return all_lines
