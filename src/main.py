import argparse
import json
import logging

from log_reader import get_folder_logs, get_zip_logs

from filesystem import FileSystem
from llm import get_last_message_content, query_json_llm, query_llm
from prompt import get_prompt
from util import create_message_id_entries

FUZZ_THRESHOLD = 70
FILTER_MAX_ENTRIES = 500


def get_error_entries(log_entries: list) -> list:
    # Create a lookup table for messages by id
    msg_lookup_by_id = {}
    for entry in log_entries:
        msg_lookup_by_id[entry.id] = entry

    # Create a list of message id, message only
    message_entries = create_message_id_entries(log_entries)
    message_json = json.dumps({"logEntries": message_entries})
    # logging.info(json.dumps(message_entries, indent=4))

    # Call get_prompt and log the result
    filter_prompt = get_prompt("filter_failures.md", message_json)
    logging.debug(filter_prompt)

    # Pass filter_prompt to query llm and parse the result as JSON
    result = query_json_llm(filter_prompt)
    logging.info(f"Failures: {len(result['failures'])}")
    logging.debug(json.dumps(result))

    # Filter log entries down to filtered list
    filtered_entries = []
    for id in result["failures"]:
        if id not in msg_lookup_by_id:
            logging.error(f"Message ID {id} not found in lookup table.")
            continue
        entry = msg_lookup_by_id[id]
        filtered_entries.append(
            {
                "message": entry.message,
                "messageID": entry.id,
            }
        )
    return filtered_entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Process log files from a specified root directory.")
    parser.add_argument("path", help="Path to the root folder containing log files or a support bundle zip")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    # Set logging level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Get all log files from the specified root folder or zip file
    log_entries = []
    fs = FileSystem(args.path)
    for file in fs.list_files():
        print(file)

    # filtered_entries = []
    # for i in range(0, len(log_entries), FILTER_MAX_ENTRIES):
    #     chunk = log_entries[i : i + FILTER_MAX_ENTRIES]
    #     filtered_entries.extend(get_error_entries(chunk))

    # message_json = json.dumps({"logEntries": filtered_entries})
    # logging.debug(json.dumps(message_json, indent=4))

    # # Query LLM for a summary of the filtered errors
    # summarize_prompt = get_prompt("summarize.md", message_json)
    # logging.debug(summarize_prompt)

    # result = query_llm(summarize_prompt)
    # msg = get_last_message_content(result)
    # logging.info(f"***********************************\n{msg}")


if __name__ == "__main__":
    main()
