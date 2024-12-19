from typing import List
from rapidfuzz import fuzz
from log_entry import LogEntry

def fuzzy_match_entries(entries: List[LogEntry], threshold: int) -> List[LogEntry]:
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
            representative = cluster["representative"]
            similarity = fuzz.ratio(entry.message, representative)
            if similarity >= threshold:
                # Add to this cluster
                cluster["entries"].append(entry)
                matched_cluster = True
                break
        if not matched_cluster:
            # Create a new cluster
            clusters.append({"representative": entry.message, "entries": [entry]})

    merged = []
    for cluster in clusters:
        # Merge files and timestamps from all entries in the cluster
        merged_entry = LogEntry(message=cluster["representative"])
        merged.append(merged_entry)
        for entry in cluster["entries"]:
            for file in entry.files:
                merged_entry.add_file(file)
            for timestamp in entry.timestamps:
                merged_entry.add_timestamp(timestamp)
        cluster["entries"] = [merged_entry]

    return merged
