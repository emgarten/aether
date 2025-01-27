from datetime import datetime
from typing import List, Dict, Set, Any

from .log_entry import LogEntry, parse_pod_info


class LogContextualizer:
    def __init__(self) -> None:
        pass

    def contextualize(self, entries: List[LogEntry]) -> List[Dict[str, Any]]:
        # Group by namespace/component
        namespace_component_sets: Dict[tuple[str, str], Set[LogEntry]] = {}
        results: List[Dict[str, Any]] = []

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
                output_entry: Dict[str, Any] = {
                    "message": entry.message,
                    "namespace": key[0],
                    "component": key[1],
                    "pods": [],
                    "occurrences": 0,
                }
                results.append(output_entry)

                for ref in entry.references:
                    info = parse_pod_info(ref.file)

                    # Filter to only references within the current namespace/component
                    if info.namespace == key[0] and info.component == key[1]:
                        output_entry["occurrences"] += 1

                        if info.pod not in output_entry["pods"]:
                            output_entry["pods"].append(info.pod)

                        if ref.timestamp:
                            if not output_entry.get("first_timestamp") or ref.timestamp < output_entry["first_timestamp"]:
                                output_entry["first_timestamp"] = ref.timestamp

                            if not output_entry.get("last_timestamp") or ref.timestamp > output_entry["last_timestamp"]:
                                output_entry["last_timestamp"] = ref.timestamp

        # Convert timestamps to strings
        for result_entry in results:
            if "first_timestamp" in result_entry:
                result_entry["first_timestamp"] = datetime_to_string(result_entry["first_timestamp"])

            if "last_timestamp" in result_entry:
                result_entry["last_timestamp"] = datetime_to_string(result_entry["last_timestamp"])

        return results


def datetime_to_string(dt: datetime) -> str:
    iso_str = dt.isoformat(timespec="microseconds")
    if iso_str.endswith("+00:00"):
        iso_str = iso_str[:-6] + "Z"
    return iso_str
