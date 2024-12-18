import re
from typing import Any, Dict, List

from log_entry import LogEntry


def create_message_id_entries(log_entries: List[LogEntry]) -> List[Dict[str, Any]]:
    """
    Create a list of objects with message and messageID properties from log entries.

    :param log_entries: A list of log entries, each containing a message.
    :return: A list of objects with 'message' and 'messageID' properties.
    """
    log_objects = []
    for entry in log_entries:
        log_objects.append({"message": entry.message, "messageID": entry.id})
    return log_objects


def extract_first_json_block(markdown_text: str) -> str:
    """
    Extracts the first JSON block from a markdown string.

    :param markdown_text: A string containing markdown content.
    :return: The content of the first JSON block, or an empty string if none is found.
    """
    match = re.search(r"```json\s*(\{.*?\})\s*```", markdown_text, re.DOTALL)
    if match:
        return match.group(1)
    return ""
