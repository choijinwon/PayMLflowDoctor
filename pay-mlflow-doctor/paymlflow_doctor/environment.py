from __future__ import annotations

import json
from importlib import metadata


def normalize_package_name(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def installed_packages() -> dict[str, str]:
    packages: dict[str, str] = {}
    for dist in metadata.distributions():
        name = dist.metadata.get("Name")
        if not name:
            continue
        packages[normalize_package_name(name)] = dist.version
    return dict(sorted(packages.items()))


def installed_packages_json() -> str:
    return json.dumps(installed_packages(), indent=2, sort_keys=True)


def installed_packages_markdown(limit: int | None = None) -> str:
    packages = installed_packages()
    items = list(packages.items())
    if limit:
        items = items[:limit]
    lines = ["# Current Python Environment", "", "| Package | Version |", "| --- | --- |"]
    for name, version in items:
        lines.append(f"| `{name}` | `{version}` |")
    if limit and len(packages) > limit:
        lines.append("")
        lines.append(f"Showing {limit} of {len(packages)} installed packages.")
    return "\n".join(lines) + "\n"
