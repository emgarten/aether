import argparse
import json
import logging

from filesystem import FileSystem
from llm import get_last_message_content, query_llm
from log_clusterer import LogClusterer
from log_contextualizer import LogContextualizer
from log_filter import LogFilter
from prompt import get_prompt

FUZZ_THRESHOLD = 70


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

    # Cluster log entries
    cl = LogClusterer(FUZZ_THRESHOLD)
    log_entries = cl.cluster_files(fs, "azure-iot-operations")
    logging.info(f"Log entries: {len(log_entries)}")

    # Filter to errors
    filter = LogFilter()
    error_entries = filter.error_entries(log_entries)
    logging.info(f"Failures: {len(error_entries)}")

    # Contextualize errors
    lc = LogContextualizer()
    context_entries = lc.contextualize(error_entries)
    logging.debug(json.dumps(context_entries, indent=4))

    # Query LLM for a summary of the filtered errors
    message_json = json.dumps({"logEntries": context_entries})
    logging.debug(json.dumps(message_json, indent=4))

    summarize_prompt = get_prompt("summarize.md", message_json)
    logging.debug(summarize_prompt)

    result = query_llm(summarize_prompt)
    msg = get_last_message_content(result)
    logging.info(f"***********************************\n{msg}")


if __name__ == "__main__":
    main()
