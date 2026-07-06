from __future__ import annotations

from pathlib import Path

from .validators import validate_project


ENV_EXAMPLE = """MLFLOW_TRACKING_URI=https://mlflow.example.internal
MLFLOW_EXPERIMENT_NAME=paymlflow-doctor-demo
MODEL_URI=models:/your-model/Staging
"""


def plan_fixes(root: str | Path) -> list[dict[str, str]]:
    report = validate_project(root)
    planned: list[dict[str, str]] = []
    for finding in report.findings:
        if finding.autofix == "create_env_example":
            planned.append({
                "id": finding.id,
                "action": "create .env.example",
                "risk": "safe",
                "detail": "Adds placeholder MLflow deployment variables without secrets.",
            })
        elif finding.autofix == "append_mlflow":
            planned.append({
                "id": finding.id,
                "action": "append mlflow>=2.0 to requirements.txt",
                "risk": "needs review",
                "detail": "Useful for demos, but production should pin the exact internally approved version.",
            })
        elif finding.autofix in {"normalize_paths", "insert_workdir", "generate_requirements"}:
            planned.append({
                "id": finding.id,
                "action": finding.autofix,
                "risk": "needs review",
                "detail": "Codex should show a diff and ask for confirmation before applying.",
            })
    return planned


def apply_safe_fixes(root: str | Path) -> list[str]:
    project_root = Path(root).expanduser().resolve()
    applied: list[str] = []
    report = validate_project(project_root)
    finding_ids = {finding.id for finding in report.findings}
    env_path = project_root / ".env.example"
    if "TRACKING_URI_MISSING" in finding_ids and not env_path.exists():
        env_path.write_text(ENV_EXAMPLE, encoding="utf-8")
        applied.append("created .env.example")
    return applied
