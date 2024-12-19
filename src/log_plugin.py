import json

from typing import Annotated
from semantic_kernel.functions.kernel_function_decorator import kernel_function
from log_reader import get_folder_logs, get_zip_logs
from util import create_message_id_entries

FUZZ_THRESHOLD = 70

class LogPlugin:
    path = ''

    def __init__ (self, path):
        self.path = path

    @kernel_function(name="supportBundleDigest", description="reads support bundle to return a clustered digest of log entries for summary.")
    def digest(self) -> Annotated[str, "a clustered digest of log entries"]:
        # Get all log files from the specified root folder or zip file
        log_entries = []
        if self.path.endswith(".zip"):
            log_entries = get_zip_logs(self.path, FUZZ_THRESHOLD)
        else:
            log_entries = get_folder_logs(self.path, FUZZ_THRESHOLD)

        # Create a lookup table for messages by id
        msg_lookup_by_id = {}
        for entry in log_entries:
            msg_lookup_by_id[entry.id] = entry

        # Create a list of message id, message only
        message_entries = create_message_id_entries(log_entries)
        message_json = json.dumps({"logEntries": message_entries})

        return message_json
