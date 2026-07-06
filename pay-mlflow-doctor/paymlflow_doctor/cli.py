from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .autofix import apply_safe_fixes, plan_fixes
from .report import to_json, to_markdown
from .validators import validate_project


def _write_or_print(content: str, output: str | None) -> None:
    if output:
        Path(output).write_text(content, encoding="utf-8")
    else:
        print(content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="paymlflow-doctor")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="Scan an MLflow project before deployment.")
    validate.add_argument("project", help="Path to the MLflow project or model directory.")
    validate.add_argument("--format", choices=["json", "markdown"], default="markdown")
    validate.add_argument("--output", help="Optional output file path.")
    validate.add_argument("--fail-on", choices=["critical", "high", "medium", "low"], default=None)
    validate.add_argument("--policy", help="Optional enterprise policy YAML file.")

    fix = sub.add_parser("fix", help="Plan or apply safe configuration fixes.")
    fix.add_argument("project")
    fix.add_argument("--apply", action="store_true", help="Apply only low-risk fixes.")
    fix.add_argument("--policy", help="Optional enterprise policy YAML file.")

    args = parser.parse_args(argv)
    if args.command == "validate":
        report = validate_project(args.project, args.policy)
        content = to_json(report) if args.format == "json" else to_markdown(report)
        _write_or_print(content, args.output)
        if args.fail_on:
            order = ["low", "medium", "high", "critical"]
            threshold = order.index(args.fail_on)
            if any(order.index(f.severity) >= threshold for f in report.findings):
                return 2
        return 0
    if args.command == "fix":
        if args.apply:
            for item in apply_safe_fixes(args.project, args.policy):
                print(item)
            return 0
        for item in plan_fixes(args.project, args.policy):
            print(f"{item['risk']}: {item['action']} ({item['id']}) - {item['detail']}")
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
