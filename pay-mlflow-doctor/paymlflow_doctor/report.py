from __future__ import annotations

import json

from .models import ScanReport


def to_json(report: ScanReport) -> str:
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False)


def to_markdown(report: ScanReport) -> str:
    lines = [
        "# PayMLflow Doctor Report",
        "",
        f"- Project: `{report.project}`",
        f"- Deployment readiness score: `{report.score}/100`",
        f"- Risk level: `{report.risk_level}`",
        f"- Files scanned: `{len(report.files_scanned)}`",
        "",
        "## Findings",
        "",
    ]
    if not report.findings:
        lines.append("No deployment-blocking environment risks were detected.")
    for index, finding in enumerate(report.findings, start=1):
        lines.extend([
            f"### {index}. {finding.title}",
            "",
            f"- ID: `{finding.id}`",
            f"- Severity: `{finding.severity}`",
            f"- File: `{finding.file}`",
            f"- Message: {finding.message}",
            f"- Recommendation: {finding.recommendation}",
            f"- Auto fix: `{finding.autofix}`",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"
