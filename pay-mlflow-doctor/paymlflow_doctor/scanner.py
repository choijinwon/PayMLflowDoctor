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


def _detect_workspace_root(project_root: Path) -> Path:
    for candidate in (project_root, *project_root.parents):
        if (candidate / ".git").exists() or (candidate / ".vscode").exists():
            return candidate
    cwd = Path.cwd().resolve()
    try:
        project_root.relative_to(cwd)
        return cwd
    except ValueError:
        return project_root.parent


def scan_project(root: str | Path) -> ScanContext:
    project_root = Path(root).expanduser().resolve()
    workspace_root = _detect_workspace_root(project_root)
    context = ScanContext(root=project_root, workspace_root=workspace_root)
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
