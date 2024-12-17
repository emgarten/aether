import hashlib

def get_hash(input_string: str) -> str:
    """
    Generate a SHA-256 hash for the given input string.

    :param input_string: The string to hash.
    :return: The hexadecimal representation of the hash.
    """
    hash_object = hashlib.sha256(input_string.encode('utf-8'))
    return hash_object.hexdigest()