import os
import sys
import argparse
from rapidfuzz import fuzz
import re

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

def process_timestamps(text):
    """
    Replace all timestamps in the string with '{TIMESTAMP}' and return the first timestamp if any exist, otherwise None.
    """
    timestamp_patterns = [
        r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z',  # ISO 8601 format
        r'\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}',          # Alternative format
    ]

    first_timestamp = None
    for pattern in timestamp_patterns:
        match = re.search(pattern, text)
        if match and not first_timestamp:
            first_timestamp = match.group(0)
        text = re.sub(pattern, '{TIMESTAMP}', text)
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
        log_lines = get_log_lines(log_file)

        # Preprocess and remove timestamps
        # processed_lines = [process_timestamps(line) for line in log_lines]
        processed_lines = log_lines

        # Cluster logs with rapidfuzz within a log file
        clusters = fuzzy_match_logs(processed_lines, FUZZ_THRESHOLD)
        for i, cluster in enumerate(clusters):
            # print("cluster: ", cluster['representative'])
            rep_lines.append(cluster['representative'])

        print(f"Log file: {log_file} lines: {len(log_lines)} -> {len(clusters)}")

    rep_clusters = fuzzy_match_logs(rep_lines, FUZZ_THRESHOLD)
    print(f"Result: {len(rep_clusters)}")
    for i, cluster in enumerate(rep_clusters):
       print(cluster['representative'])

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
