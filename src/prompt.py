import os


def get_prompt(filename: str, input_string: str) -> str:
    """
    Reads the content of a file from the prompt directory, appends a few new lines,
    then appends the input string, and returns the combination.

    :param filename: The name of the file to read.
    :param input_string: The string to append to the file content.
    :return: The combined content of the file and the input string.
    :raises FileNotFoundError: If the file does not exist.
    :raises IOError: If there is an error reading the file.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        file_path = os.path.join(parent_dir, "prompt", filename)

        with open(file_path, "r", encoding="utf-8") as file:
            file_content = file.read()

        # Append a few new lines and then the input string
        combined_content = file_content + "\n\n\n" + input_string
        return combined_content
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{filename}' does not exist in the prompt directory.")
    except IOError as e:
        raise IOError(f"An error occurred while reading the file '{filename}': {e}")
