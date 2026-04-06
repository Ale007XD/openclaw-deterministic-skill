from typing import List, Dict


def merge_tool_results(results: List[Dict]) -> List[Dict]:
    unique = {}

    for r in results:
        key = (r.get("tool_name"), r.get("call_id"))

        if key in unique and unique[key] != r:
            raise ValueError(f"Conflict in tool results: {key}")

        unique[key] = r

    return sorted(
        list(unique.values()),
        key=lambda r: (r.get("tool_name", ""), r.get("call_id", ""))
    )
