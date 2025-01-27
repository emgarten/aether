import json
import logging
from typing import Any, Dict, List

from .llm import query_json_llm
from .log_entry import LogEntry
from .prompt import get_prompt

FILTER_MAX_ENTRIES = 500


class LogFilter:
    def __init__(self) -> None:
        pass

    def error_entries(self, log_entries: List[LogEntry]) -> List[LogEntry]:
        # Page the entries through the LLM
        filtered_entries: List[LogEntry] = []
        for i in range(0, len(log_entries), FILTER_MAX_ENTRIES):
            chunk = log_entries[i : i + FILTER_MAX_ENTRIES]
            filtered_entries.extend(get_error_entries(chunk))

        return filtered_entries


def get_error_entries(log_entries: List[LogEntry]) -> List[LogEntry]:
    # Create a lookup table for messages by id
    msg_lookup_by_id: Dict[str, LogEntry] = {}
    for entry in log_entries:
        msg_lookup_by_id[entry.get_id()] = entry

    # Create a list of message id, message only
    message_entries = create_message_id_entries(log_entries)
    message_json = json.dumps({"logEntries": message_entries})
    # logging.info(json.dumps(message_entries, indent=4))

    # Call get_prompt and log the result
    filter_prompt = get_prompt("filter_failures.md", message_json)
    logging.debug(filter_prompt)

    # Pass filter_prompt to query llm and parse the result as JSON
    result = query_json_llm(filter_prompt)
    logging.debug(json.dumps(result))

    # Filter log entries down to filtered list
    filtered_entries: List[LogEntry] = []
    for id in result["failures"]:
        if id not in msg_lookup_by_id:
            logging.error(f"Message ID {id} not found in lookup table.")
            continue
        entry = msg_lookup_by_id[id]
        filtered_entries.append(entry)
    return filtered_entries


def create_message_id_entries(log_entries: List[LogEntry]) -> List[Dict[str, Any]]:
    """
    Create a list of objects with message and messageID properties from log entries.

    :param log_entries: A list of log entries, each containing a message.
    :return: A list of objects with 'message' and 'messageID' properties.
    """
    log_objects: List[Dict[str, Any]] = []
    for entry in log_entries:
        log_objects.append({"message": entry.message, "messageID": entry.get_id()})
    return log_objects
