import os
import re
import hdbscan
from sentence_transformers import SentenceTransformer
import numpy as np
import argparse
from collections import Counter

def read_logs_from_folder(folder_path):
    """
    Reads all files in the given folder and extracts log lines from each file.
    :param folder_path: Path to the folder containing log files.
    :return: A list of log lines.
    """
    logs = []
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                logs.extend(file.readlines())  # Read lines from each file
    return [log.strip() for log in logs if log.strip()]  # Remove empty lines and whitespace

def preprocess_logs(logs):
    """
    Preprocess logs to remove timestamps and normalize the text for better clustering.
    :param logs: List of raw log lines.
    :return: List of preprocessed log lines.
    """
    preprocessed_logs = []
    for log in logs:
        # Remove syslog-style priority levels and timestamps, e.g., "<6>2024-09-10T23:19:14.726Z"
        log = re.sub(r'<\d+>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z', '', log)
        # Remove additional common timestamp formats (if needed)
        log = re.sub(r'\b\d{4}-\d{2}-\d{2}\b', '', log)  # Remove "YYYY-MM-DD"
        log = re.sub(r'\b\d{2}:\d{2}(:\d{2})?\b', '', log)  # Remove "HH:MM:SS" or "HH:MM"
        log = re.sub(r'\[.*?\]', '', log)  # Remove text in square brackets (e.g., [mq@311 tid="9"])
        log = re.sub(r'\s+', ' ', log).strip()  # Normalize spaces
        preprocessed_logs.append(log)
    return preprocessed_logs

def cluster_logs(folder_path):
    """
    Clusters logs using HDBSCAN and SentenceTransformers.
    :param folder_path: Path to the folder containing log files.
    """
    # Step 1: Load a pre-trained SentenceTransformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Step 2: Read logs from the folder
    raw_logs = read_logs_from_folder(folder_path)
    if not raw_logs:
        print("No logs found in the folder.")
        return

    # Step 3: Preprocess logs (remove timestamps and normalize text)
    logs = preprocess_logs(raw_logs)

    # Step 4: Generate embeddings for the logs
    embeddings = model.encode(logs)

    # Step 5: Apply HDBSCAN clustering with adjusted parameters for grouping more logs
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2)
    cluster_labels = clusterer.fit_predict(embeddings)

    # Step 6: Output clustering results
    print("Clustering Results:")
    clusters = {}
    for i, label in enumerate(cluster_labels):
        log = logs[i]
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(log)

    for cluster_id, cluster_logs in clusters.items():
        if cluster_id == -1:
            print("\nNoise (Unclustered Logs):")
        else:
            print(f"\nCluster {cluster_id}:")
        for log in cluster_logs:
            print(f"  - {log}")

    # Step 7: Identify and print rarest 10 log entries
    print("\nRarest 10 Log Entries:")
    log_counts = Counter(logs)
    rarest_logs = log_counts.most_common()[:-11:-1]  # Get 10 least common logs
    for log, count in rarest_logs:
        print(f"  - {log} (Count: {count})")

if __name__ == "__main__":
    # Parse the folder path as a command-line argument
    parser = argparse.ArgumentParser(description="Cluster logs from files in a folder.")
    parser.add_argument(
        "folder_path",
        type=str,
        help="Path to the folder containing log files.",
    )
    args = parser.parse_args()

    # Call the clustering function with the provided folder path
    cluster_logs(args.folder_path)
