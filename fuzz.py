import os
import sys
import argparse
from rapidfuzz import fuzz

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

def read_all_logs(log_files):
    """
    Read all lines from the provided log files into a single list.
    """
    all_lines = []
    for log_file in log_files:
        with open(log_file, 'r', encoding='utf-8', errors='replace') as f:
            for line in f:
                line = line.strip()
                if line:  # ignore empty lines
                    all_lines.append(line)
    return all_lines

def cluster_logs(log_lines, threshold):
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
    parser = argparse.ArgumentParser(description="Cluster similar log entries to show unique log lines.")
    parser.add_argument("log_dir", help="Path to the directory containing log files")
    parser.add_argument("--threshold", type=int, default=90, 
                        help="Similarity threshold (0-100) for clustering (default: 90)")
    args = parser.parse_args()
    
    if not os.path.isdir(args.log_dir):
        print("Invalid directory path.")
        sys.exit(1)
    
    # Get all log files
    log_files = get_log_files(args.log_dir)
    if not log_files:
        print("No log files found in the specified directory.")
        sys.exit(0)
    
    # Read all lines
    lines = read_all_logs(log_files)
    if not lines:
        print("No log entries found.")
        sys.exit(0)
    
    # Cluster logs
    clusters = cluster_logs(lines, args.threshold)
    
    # Print a representative from each cluster
    print("Found {} unique clusters:".format(len(clusters)))
    for idx, cluster in enumerate(clusters, start=1):
        print(f"Cluster {idx}: {cluster['representative']}")

if __name__ == "__main__":
    main()
