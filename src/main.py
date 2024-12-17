import argparse
import json
import logging

from cluster import fuzzy_match_entries
from log_reader import get_log_entries, get_log_files, get_log_lines

FUZZ_THRESHOLD = 70

logging.basicConfig(level=logging.INFO)


def main() -> None:
    parser = argparse.ArgumentParser(description="Process log files from a specified root directory.")
    parser.add_argument("root_folder", help="Path to the root folder containing log files")
    args = parser.parse_args()

    # Get all log files from the specified root folder
    log_files = get_log_files(args.root_folder)
    rep_lines = []
    logging.debug("Log files found:", log_files)

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
            # logging.info("cluster: ", cluster['representative'])
            rep_lines.append(cluster)

        logging.debug(f"Log file: {log_file} lines: {len(log_entries)} -> {len(merged_log_entries)}")

    merged_rep_lines = fuzzy_match_entries(rep_lines, FUZZ_THRESHOLD)
    logging.info(f"Result: {len(merged_rep_lines)}")
    # Convert merged_rep_lines to JSON and print it formatted
    log_entries = []
    for entry in merged_rep_lines:
        entry_dict = entry.to_dict()
        log_entries.append(entry_dict)

    log_json = {"logEntries": log_entries}
    logging.info(json.dumps(log_json, indent=4))


if __name__ == "__main__":
    main()
