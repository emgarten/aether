from typing import List

from log_entry import LogEntry


class LogContextualizer:
    def __init__(self):
        pass

    def contextualize(self, entries: List[LogEntry]):
        # Use get_pod_info to get the namespace, component, pod, and container from the files for the entry
        # Group entries by namespace/component
        # Have an array of pods where the entry was seen

        # Create a dictionary for each group, add the message to the dictionary
        # Add in the namespace, component, and list of pods to the dictionary

        # Add total occurrence count

        # Add first timestamp

        # Add last timestamp

        #

        pass
