from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


SEVERITY_SCORE = {
    "critical": 35,
    "high": 20,
    "medium": 10,
    "low": 4,
    "info": 0,
}


@dataclass(frozen=True)
class Finding:
    id: str
    title: str
    severity: str
    file: str
    message: str
    recommendation: str
    autofix: str = "none"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity,
            "file": self.file,
            "message": self.message,
            "recommendation": self.recommendation,
            "autofix": self.autofix,
        }


@dataclass
class ScanContext:
    root: Path
    workspace_root: Path
    files: dict[str, Path] = field(default_factory=dict)
    text: dict[str, str] = field(default_factory=dict)

    def rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.workspace_root))
        except ValueError:
            return str(path)


@dataclass
class ScanReport:
    project: str
    score: int
    risk_level: str
    files_scanned: list[str]
    findings: list[Finding]
    summary: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "project": self.project,
            "score": self.score,
            "risk_level": self.risk_level,
            "files_scanned": self.files_scanned,
            "summary": self.summary,
            "findings": [finding.to_dict() for finding in self.findings],
        }
