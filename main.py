import os
import sys
import argparse
from rapidfuzz import fuzz
from typing import List
import re
import json
from log_entry import LogEntry

FUZZ_THRESHOLD = 70

def get_log_files(directory):
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

def get_log_lines(log_file):
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

def get_log_entries(log_file):
    log_entries = []
    with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.strip()
            if line:  # ignore empty lines
                timestamp = get_timestamp(line)
                log_entry = LogEntry(message=line)
                log_entry.add_file(log_file)  # Add the log file name
                if timestamp:
                    log_entry.add_timestamp(timestamp)
                log_entries.append(log_entry)
    return log_entries

def get_timestamp(text):
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

def fuzzy_match_logs(log_lines, threshold):
    """
    Cluster the log lines based on a string similarity threshold.
    This uses a simple greedy approach:
      - Initialize an empty list of clusters.
      - For each log line:
        * Compare it with representative lines of existing clusters.
        * If it matches a cluster's representative line with similarity >= threshold,
          add it to that cluster.
        * Otherwise, create a new cluster.

    Note: This is O(N^2) in worst case and may be slow for very large logs.
    For efficiency, consider using a more advanced technique or indexing.
    """
    clusters = []
    for line in log_lines:
        matched_cluster = False
        for cluster in clusters:
            # Compare against the cluster's representative line
            representative = cluster['representative']
            similarity = fuzz.ratio(line, representative)
            if similarity >= threshold:
                # Add to this cluster
                cluster['lines'].append(line)
                matched_cluster = True
                break
        if not matched_cluster:
            # Create a new cluster
            clusters.append({
                'representative': line,
                'lines': [line]
            })
    return clusters

def fuzzy_match_entries(entries, threshold):
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
    clusters = []
    for entry in entries:
        matched_cluster = False
        for cluster in clusters:
            # Compare against the cluster's representative message
            representative = cluster['representative']
            similarity = fuzz.ratio(entry.message, representative)
            if similarity >= threshold:
                # Add to this cluster
                cluster['entries'].append(entry)
                matched_cluster = True
                break
        if not matched_cluster:
            # Create a new cluster
            clusters.append({
                'representative': entry.message,
                'entries': [entry]
            })

    merged = []
    for cluster in clusters:
        # Merge files and timestamps from all entries in the cluster
        merged_entry = LogEntry(message=cluster['representative'])
        merged.append(merged_entry)
        for entry in cluster['entries']:
            for file in entry.files:
                merged_entry.add_file(file)
            for timestamp in entry.timestamps:
                merged_entry.add_timestamp(timestamp)
        cluster['entries'] = [merged_entry]

    return merged

def main():
    parser = argparse.ArgumentParser(description="Process log files from a specified root directory.")
    parser.add_argument("root_folder", help="Path to the root folder containing log files")
    args = parser.parse_args()

    # Get all log files from the specified root folder
    log_files = get_log_files(args.root_folder)
    rep_lines = []
    print("Log files found:", log_files)
    for log_file in log_files:
        # Read all lines from the log file
        # log_lines = get_log_lines(log_file)
        log_entries = get_log_entries(log_file)

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
    json_output = json.dumps(log_json, indent=4)
    print(json_output)

    # Discover log files
    # Load log file
    # Preprocess and remove timestamps
    # Find first/last timestamp to get time range
    # Cluster logs with rapidfuzz within a log file
    # Take one line from each cluster, build log file info, and time range
    # Combine across all log files
    # Query to filter to errors
    # Summarize all errors with additional instructions on how to prioritize errors

if __name__ == "__main__":
    main()
