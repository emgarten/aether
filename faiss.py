import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# ---------------------------------------
# Configuration
# ---------------------------------------
LOGS_FOLDER = "/mnt/c/tmp/logs-xs"  # Update to point to your log directory
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
FUZZINESS_THRESHOLD = 0.7  # Adjust this value. Lower means stricter uniqueness criteria.

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
    This is where you could remove timestamps, etc."""
    # Example (commented out):
    # import re
    # lines = [re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{3}Z','', line) for line in lines]
    return lines

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

    print(f"Total log lines: {len(lines)}")

    # Create embeddings
    model = SentenceTransformer(MODEL_NAME)
    embeddings = model.encode(lines, convert_to_numpy=True)

    # FAISS expects float32
    embeddings = embeddings.astype(np.float32)

    print(f"Encoding complete")

    # Initialize FAISS index
    # We'll use a simple IndexFlatL2 for cosine or L2 similarity searching.
    # Note: For cosine similarity, we often normalize embeddings. We'll do that here.
    faiss.normalize_L2(embeddings)
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)

    unique_messages = []
    unique_embeddings = []

    print(f"FAISS index complete")

    # We'll iterate through all embeddings and maintain a dynamic FAISS index of unique messages.
    for i, emb in enumerate(embeddings):
        if len(unique_embeddings) == 0:
            # First message is always unique
            unique_messages.append(lines[i])
            unique_embeddings.append(emb.reshape(1, -1))
            index.add(emb.reshape(1, -1))
        else:
            # Check nearest neighbor in current index
            D, I = index.search(emb.reshape(1, -1), 1)
            # D is the array of distances to the nearest neighbor(s). 
            # For normalized embeddings, distance is related to similarity:
            # If using L2 distance on normalized vectors, smaller = closer.
            # Convert L2 distance to a "similarity" measure or use it directly as a threshold.
            # Typically, for normalized vectors, L2 distance of 0 means identical, and up to ~2 is quite distinct.
            # For a fuzziness threshold, you might set it based on experimentation.
            #
            # Example: 
            # - With normalized embeddings, two identical vectors have distance ~0.
            # - Completely different ones could approach a distance of 2.0.
            # A threshold of ~0.7 might mean fairly close in semantic space.
            #
            # If D[0][0] > FUZZINESS_THRESHOLD, we consider it a new unique message.
            if D[0][0] > FUZZINESS_THRESHOLD:
                unique_messages.append(lines[i])
                unique_embeddings.append(emb.reshape(1, -1))
                index.add(emb.reshape(1, -1))

    # Print unique messages
    print("Unique Messages Beyond Specified Fuzziness:")
    for msg in unique_messages:
        print(msg)

if __name__ == "__main__":
    main()
