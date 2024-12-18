import argparse
import json
import logging

from cluster import fuzzy_match_entries
from log_reader import get_log_entries, get_log_files, get_log_lines
from openai import query_json_llm, query_llm
from prompt import get_prompt
from util import create_message_id_entries

FUZZ_THRESHOLD = 70


def main() -> None:
    parser = argparse.ArgumentParser(description="Process log files from a specified root directory.")
    parser.add_argument("root_folder", help="Path to the root folder containing log files")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

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

    # Create a lookup table for messages by id
    msg_lookup_by_id = {}
    for entry in merged_rep_lines:
        msg_lookup_by_id[entry.id] = entry

    # Create a list of message id, message only
    message_entries = create_message_id_entries(merged_rep_lines)
    message_json = json.dumps({"logEntries": message_entries})
    # logging.info(json.dumps(message_entries, indent=4))

    # Call get_prompt and log the result
    filter_prompt = get_prompt("filter_failures.md", message_json)
    logging.debug(filter_prompt)

    # Pass filter_prompt to query llm and parse the result as JSON
    result = query_json_llm(filter_prompt)
    logging.info(f"Failures: {len(result['failures'])} Info: {len(result['info'])} Total recv: {len(result['failures']) + len(result['info'])} Original total: {len(message_entries)}")
    logging.info(json.dumps(result))

    # Filter log entries down to filtered list
    filtered_entries = []
    for id in result["failures"]:
        entry = msg_lookup_by_id[id]
        filtered_entries.append(
            {
                "message": entry.message,
                "messageID": entry.id,
            }
        )

    message_json = json.dumps({"logEntries": filtered_entries})
    logging.debug(json.dumps(message_json, indent=4))

    # Query LLM for a summary of the filtered errors
    summarize_prompt = get_prompt("summarize.md", message_json)
    logging.debug(summarize_prompt)

    result = query_llm(summarize_prompt)
    logging.info(f"***********************************\n{result}")


if __name__ == "__main__":
    main()
