import re


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
