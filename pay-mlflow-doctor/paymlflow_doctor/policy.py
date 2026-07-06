from __future__ import annotations

from pathlib import Path


Policy = dict[str, list[str]]


def load_policy(path: str | Path | None) -> Policy:
    if not path:
        return {}
    policy_path = Path(path).expanduser().resolve()
    policy: Policy = {}
    current_key: str | None = None
    for raw_line in policy_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_key = line[:-1].strip()
            policy.setdefault(current_key, [])
            continue
        if current_key and line.lstrip().startswith("- "):
            value = line.lstrip()[2:].strip().strip("'\"")
            policy[current_key].append(value)
    return policy
