from __future__ import annotations

from pathlib import Path

from .models import ScanContext


TARGET_FILES = [
    "requirements.txt",
    "conda.yaml",
    "conda.yml",
    "pyproject.toml",
    "Dockerfile",
    "MLmodel",
    "model.yaml",
    "config.yaml",
    "config.yml",
    ".env",
    ".env.example",
    "kserve.yaml",
    "kserve.yml",
    "deployment.yaml",
    "deployment.yml",
    "serving.yaml",
    "serving.yml",
]

EXCLUDE_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}


def scan_project(root: str | Path) -> ScanContext:
    project_root = Path(root).expanduser().resolve()
    context = ScanContext(root=project_root)
    for filename in TARGET_FILES:
        for path in project_root.rglob(filename):
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            rel = context.rel(path)
            context.files[rel] = path
            try:
                context.text[rel] = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                context.text[rel] = path.read_text(encoding="utf-8", errors="replace")
    for path in project_root.rglob("*.py"):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        rel = context.rel(path)
        if rel in context.files:
            continue
        context.files[rel] = path
        try:
            context.text[rel] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            context.text[rel] = path.read_text(encoding="utf-8", errors="replace")
    return context
