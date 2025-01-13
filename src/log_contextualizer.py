from typing import List

from log_entry import LogEntry, parse_pod_info


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

        # return a list of the dictionaries

        pass

    def create_namespace_component_sets(self, entries: List[LogEntry]) -> List[dict]:
        # Group by namespace/component
        namespace_component_sets = {}
        results = []

        for entry in entries:
            for ref in entry.references:
                info = parse_pod_info(ref.file)

                key = (info.namespace, info.component)
                if key not in namespace_component_sets:
                    namespace_component_sets[key] = set()
                namespace_component_sets[key].add(entry)

        # Create filtered entries for each namespace/component
        for key, entry_set in namespace_component_sets.items():
            for entry in entry_set:
                output_entry = {
                    "message": entry.message,
                    "namespace": key[0],
                    "component": key[1],
                    "pods": []
                }
                results.append(output_entry)

                for ref in entry.references:
                    info = parse_pod_info(ref.file)
                    if info.namespace == key[0] and info.component == key[1]:
                        if info.pod not in output_entry["pods"]:
                            output_entry["pods"].append(info.pod)
                        
                        

        return results