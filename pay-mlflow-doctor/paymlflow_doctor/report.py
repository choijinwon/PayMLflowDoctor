from __future__ import annotations

import json

from .models import ScanReport


def to_json(report: ScanReport) -> str:
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)


def _cell(value: object) -> str:
    text = str(value).replace("\n", " ").replace("|", "\\|")
    return text


def _release_decision(risk_level: str) -> str:
    if risk_level == "blocked":
        return "Stop deployment"
    if risk_level == "high":
        return "Hold release until high risks are fixed"
    if risk_level == "medium":
        return "Proceed only with owner approval"
    return "Ready for controlled deployment"


def _autofix_label(autofix: str) -> str:
    if autofix == "none":
        return "No"
    if autofix == "requires_confirmation":
        return "Requires confirmation"
    return "Safe" if autofix in {"create_env_example"} else autofix


def to_markdown(report: ScanReport) -> str:
    lines = [
        "# PayMLflow Doctor Report",
        "",
        "## Deployment Summary",
        "",
        "| Item | Value |",
        "| --- | --- |",
        f"| Project | `{_cell(report.project)}` |",
        f"| Deployment Readiness Score | `{report.score}/100` |",
        f"| Risk Level | `{report.risk_level}` |",
        f"| Files Scanned | `{len(report.files_scanned)}` |",
        f"| Release Decision | {_release_decision(report.risk_level)} |",
        "",
        "## Severity Summary",
        "",
        "| Severity | Count | Meaning |",
        "| --- | ---: | --- |",
        f"| Critical | {report.summary.get('critical', 0)} | Deployment likely fails or violates release safety. |",
        f"| High | {report.summary.get('high', 0)} | Must be fixed before production deployment. |",
        f"| Medium | {report.summary.get('medium', 0)} | Operational risk exists and needs owner review. |",
        f"| Low | {report.summary.get('low', 0)} | Cleanup or hardening recommended. |",
        f"| Info | {report.summary.get('info', 0)} | Informational context. |",
        "",
        "## Findings",
        "",
        "| No | Severity | Check ID | File | Finding | Recommendation | Auto Fix |",
        "| ---: | --- | --- | --- | --- | --- | --- |",
    ]
    if not report.findings:
        lines.append("| - | - | - | - | No deployment-blocking environment risks were detected. | - | - |")
    for index, finding in enumerate(report.findings, start=1):
        lines.append(
            "| "
            f"{index} | "
            f"{_cell(finding.severity)} | "
            f"`{_cell(finding.id)}` | "
            f"`{_cell(finding.file)}` | "
            f"{_cell(finding.message)} | "
            f"{_cell(finding.recommendation)} | "
            f"{_autofix_label(finding.autofix)} |"
        )
    lines.extend([
        "",
        "## Fix Plan",
        "",
        "| Priority | Action | Risk |",
        "| ---: | --- | --- |",
    ])
    fix_count = 0
    for finding in report.findings:
        if finding.severity not in {"critical", "high", "medium"}:
            continue
        fix_count += 1
        lines.append(
            "| "
            f"{fix_count} | "
            f"{_cell(finding.recommendation)} | "
            f"{_cell(finding.severity)} |"
        )
    if fix_count == 0:
        lines.append("| - | No action required. | low |")
    return "\n".join(lines).rstrip() + "\n"
