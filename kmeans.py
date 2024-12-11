import os
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
import numpy as np

# ---------------------------------------
# Configuration
# ---------------------------------------
LOGS_FOLDER = "/mnt/c/tmp/logs-xs"  # Update to point to your log directory
N_CLUSTERS = 10  # Initial guess of how many clusters to form. Adjust as needed.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# ---------------------------------------
# Helper Functions
# ---------------------------------------
def load_logs(logs_folder: str):
    """Load all lines from log files in the specified folder."""
    all_lines = []
    for filename in os.listdir(logs_folder):
        if filename.endswith(".log") or filename.endswith(".txt"):
            file_path = os.path.join(logs_folder, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        all_lines.append(line)
    return all_lines

def preprocess_lines(lines):
    """Preprocess lines if needed. For now, just return as is.
    Could remove timestamps, known variable fields, etc."""
    # Example: Remove timestamps that match a certain pattern, or pod names if known patterns exist.
    # This is a placeholder where you might add regex replacements:
    # import re
    # lines = [re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z','', line) for line in lines]
    return lines

def estimate_clusters(num_lines):
    """Heuristic to choose number of clusters based on number of lines.
    If too large, increase cluster count. This is just a heuristic."""
    if num_lines < 50:
        return min(num_lines, 5)
    elif num_lines < 500:
        return 10
    elif num_lines < 2000:
        return 20
    else:
        return 50

# ---------------------------------------
# Main Execution
# ---------------------------------------
def main():
    # Load and preprocess lines
    lines = load_logs(LOGS_FOLDER)
    lines = preprocess_lines(lines)

    if not lines:
        print("No log lines found.")
        return

    # Dynamically pick cluster count if desired
    # N_CLUSTERS = estimate_clusters(len(lines))

    # Create embeddings
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(lines, convert_to_numpy=True)

    # Cluster embeddings
    kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init="auto")
    labels = kmeans.fit_predict(embeddings)

    # For each cluster, pick a representative line.
    # A simple approach: use the line closest to the cluster center as representative.
    cluster_centers = kmeans.cluster_centers_

    # Find representative lines by distance to cluster center
    unique_representatives = []
    for cluster_id in range(N_CLUSTERS):
        cluster_indices = np.where(labels == cluster_id)[0]
        if len(cluster_indices) == 0:
            continue
        # Compute distance to cluster center
        cluster_embeddings = embeddings[cluster_indices]
        distances = np.linalg.norm(cluster_embeddings - cluster_centers[cluster_id], axis=1)
        closest_idx = cluster_indices[np.argmin(distances)]
        representative_line = lines[closest_idx]
        unique_representatives.append(representative_line)

    print("Unique Clustered Messages:")
    for i, rep_line in enumerate(unique_representatives, start=1):
        print(f"Cluster {i}: {rep_line}")

if __name__ == "__main__":
    main()
