import os
import sys
import argparse
from rapidfuzz import fuzz
from typing import List, Dict, Optional
import re
import json
from log_entry import LogEntry
import hashlib
from shelved_cache import PersistentCache
from cachetools import LRUCache
from cluster import fuzzy_match_entries

FUZZ_THRESHOLD = 70
CACHE_FILENAME = ".shelved.main.dat"

_cache = PersistentCache(LRUCache, filename=CACHE_FILENAME, maxsize=1024)


def get_log_files(directory: str) -> List[str]:
    """
    Recursively get all files in the directory that could be considered log files.
    For simplicity, we consider all files ending with '.log' as log files.
    """
    log_files = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.lower().endswith('.log'):
                log_files.append(os.path.join(root, f))
    return log_files

def get_log_lines(log_file: str) -> List[str]:
    """
    Read all lines from the provided log file into a list.
    """
    all_lines = []
    with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
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
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z',  # ISO 8601 format
        r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',          # Alternative format
        r'\d{2}:\d{2}:\d{2}\.\d{6}',                     # format: HH:MM:SS.microseconds
    ]

    first_timestamp = None
    for pattern in timestamp_patterns:
        match = re.search(pattern, text)
        if match and not first_timestamp:
            first_timestamp = match.group(0)
    return first_timestamp

def main() -> None:
    parser = argparse.ArgumentParser(description="Process log files from a specified root directory.")
    parser.add_argument("root_folder", help="Path to the root folder containing log files")
    args = parser.parse_args()

    # Get all log files from the specified root folder
    log_files = get_log_files(args.root_folder)
    rep_lines = []
    # print("Log files found:", log_files)

    for log_file in log_files:
        # Read all lines from the log file
        log_lines = get_log_lines(log_file)
        log_entries = get_log_entries(log_lines, log_file)

        # Preprocess and remove timestamps
        # processed_lines = [get_timestamp(line) for line in log_lines]
        # processed_lines = log_lines

        # Cluster logs with rapidfuzz within a log file
        merged_log_entries = fuzzy_match_entries(log_entries, FUZZ_THRESHOLD)
        for i, cluster in enumerate(merged_log_entries):
            # print("cluster: ", cluster['representative'])
            rep_lines.append(cluster)

        print(f"Log file: {log_file} lines: {len(log_entries)} -> {len(merged_log_entries)}")

    merged_rep_lines = fuzzy_match_entries(rep_lines, FUZZ_THRESHOLD)
    print(f"Result: {len(merged_rep_lines)}")
    # Convert merged_rep_lines to JSON and print it formatted
    log_entries = []
    for entry in merged_rep_lines:
        entry_dict = entry.to_dict()
        log_entries.append(entry_dict)

    log_json = {
        "logEntries": log_entries
    }

if __name__ == "__main__":
    main()
