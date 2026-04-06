from typing import List, Dict


def merge_tool_results(results: List[Dict]) -> List[Dict]:
    unique = {
        (r.get("tool_name"), r.get("call_id")): r
        for r in results
    }
    return sorted(
        unique.values(),
        key=lambda r: (r.get("tool_name", ""), r.get("call_id", ""))
    )
