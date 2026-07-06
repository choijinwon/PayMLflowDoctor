from __future__ import annotations

import re
from pathlib import Path

from .models import Finding, SEVERITY_SCORE, ScanContext, ScanReport
from .policy import Policy, load_policy
from .scanner import scan_project


def _find_file(context: ScanContext, suffix: str) -> tuple[str, str] | None:
    for rel, text in context.text.items():
        if rel.endswith(suffix):
            return rel, text
    return None


def _python_versions(context: ScanContext) -> dict[str, str]:
    versions: dict[str, str] = {}
    conda = _find_file(context, "conda.yaml") or _find_file(context, "conda.yml")
    if conda:
        match = re.search(r"python\s*=\s*([0-9]+(?:\.[0-9]+)?)", conda[1])
        if match:
            versions[conda[0]] = match.group(1)
    docker = _find_file(context, "Dockerfile")
    if docker:
        match = re.search(r"FROM\s+python:([0-9]+(?:\.[0-9]+)?)", docker[1], re.I)
        if match:
            versions[docker[0]] = match.group(1)
    mlmodel = _find_file(context, "MLmodel")
    if mlmodel:
        match = re.search(r"python_version:\s*['\"]?([0-9]+(?:\.[0-9]+)?)", mlmodel[1])
        if match:
            versions[mlmodel[0]] = match.group(1)
    pyproject = _find_file(context, "pyproject.toml")
    if pyproject:
        match = re.search(r"requires-python\s*=\s*['\"]([^'\"]+)", pyproject[1])
        if match:
            versions[pyproject[0]] = match.group(1)
    return versions


def _has_env_key(context: ScanContext, key: str) -> bool:
    for rel, text in context.text.items():
        if Path(rel).name in {".env", ".env.example", "config.yaml", "config.yml"}:
            if re.search(rf"(^|\n)\s*{re.escape(key)}\s*[:=]", text):
                return True
    return False


def _add_missing_core_files(context: ScanContext, findings: list[Finding]) -> None:
    present_names = {Path(rel).name for rel in context.files}
    if "MLmodel" not in present_names:
        findings.append(Finding(
            "MLFLOW_MLMODEL_MISSING",
            "MLmodel file is missing",
            "critical",
            ".",
            "MLflow model flavor metadata was not found, so serving compatibility cannot be verified.",
            "Export or copy the MLflow MLmodel file into the model artifact directory before deployment.",
        ))
    if not ({"requirements.txt", "conda.yaml", "conda.yml", "pyproject.toml"} & present_names):
        findings.append(Finding(
            "PYTHON_ENV_SPEC_MISSING",
            "Python environment specification is missing",
            "critical",
            ".",
            "No requirements.txt, conda.yaml, or pyproject.toml was found.",
            "Add a pinned Python dependency file generated from the training or serving environment.",
            "generate_requirements",
        ))
    if "Dockerfile" not in present_names:
        findings.append(Finding(
            "DOCKERFILE_MISSING",
            "Dockerfile is missing",
            "medium",
            ".",
            "Container build configuration was not found.",
            "Add a minimal Dockerfile or document the managed serving runtime used by KServe.",
        ))


def _validate_python(context: ScanContext, findings: list[Finding]) -> None:
    versions = _python_versions(context)
    normalized = {k: re.search(r"[0-9]+(?:\.[0-9]+)?", v).group(0) for k, v in versions.items() if re.search(r"[0-9]+(?:\.[0-9]+)?", v)}
    if len(set(normalized.values())) > 1:
        findings.append(Finding(
            "PYTHON_VERSION_MISMATCH",
            "Python versions do not match",
            "high",
            ", ".join(normalized.keys()),
            f"Detected inconsistent Python versions: {normalized}.",
            "Choose one serving Python version and align conda.yaml, Dockerfile, MLmodel, and pyproject.toml.",
            "requires_confirmation",
        ))


def _validate_requirements(context: ScanContext, findings: list[Finding]) -> None:
    req = _find_file(context, "requirements.txt")
    if not req:
        return
    rel, text = req
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]
    if lines and not any(line.lower().startswith("mlflow") for line in lines):
        findings.append(Finding(
            "MLFLOW_DEPENDENCY_MISSING",
            "mlflow dependency is missing",
            "high",
            rel,
            "requirements.txt does not include mlflow, but an MLflow project is being validated.",
            "Add a pinned mlflow version compatible with the training and serving runtime.",
            "append_mlflow",
        ))
    unpinned = [line for line in lines if not re.search(r"(==|~=|>=|<=)", line) and "://" not in line]
    if unpinned:
        findings.append(Finding(
            "UNPINNED_DEPENDENCIES",
            "Unpinned dependencies reduce reproducibility",
            "medium",
            rel,
            f"Unpinned packages detected: {', '.join(unpinned[:8])}.",
            "Pin production serving dependencies to exact versions for reproducible financial AI deployment.",
            "requires_confirmation",
        ))


def _validate_uris_and_paths(context: ScanContext, findings: list[Finding]) -> None:
    if not _has_env_key(context, "MLFLOW_TRACKING_URI"):
        findings.append(Finding(
            "TRACKING_URI_MISSING",
            "MLFLOW_TRACKING_URI is not declared",
            "high",
            ".env.example",
            "The MLflow tracking endpoint is not visible in env/config files.",
            "Add MLFLOW_TRACKING_URI to .env.example and deployment secret documentation.",
            "create_env_example",
        ))
    for rel, text in context.text.items():
        if Path(rel).name in {"model.yaml", "config.yaml", "config.yml"}:
            if re.search(r"model_uri\s*:\s*['\"]?file:", text):
                findings.append(Finding(
                    "LOCAL_MODEL_URI",
                    "Model URI points to a local file path",
                    "high",
                    rel,
                    "Local file model_uri values usually fail after containerization or KServe deployment.",
                    "Use models:/, runs:/, s3://, gs://, or a platform artifact URI reachable from the serving cluster.",
                    "requires_confirmation",
                ))
            if "\\" in text:
                findings.append(Finding(
                    "WINDOWS_PATH_IN_CONFIG",
                    "Windows path separator detected",
                    "medium",
                    rel,
                    "Backslash paths can break in Linux containers and Kubernetes pods.",
                    "Use POSIX-style paths or URI schemes for cross-platform deployment.",
                    "normalize_paths",
                ))
    mlmodel = _find_file(context, "MLmodel")
    if mlmodel:
        rel, text = mlmodel
        for match in re.finditer(r"(?:path|data):\s*([^\n]+)", text):
            raw_path = match.group(1).strip().strip("'\"")
            if "://" not in raw_path:
                candidate = context.files[rel].parent / raw_path
                if raw_path and not raw_path.endswith((".yaml", ".yml")) and not candidate.exists():
                    findings.append(Finding(
                        "ARTIFACT_PATH_MISSING",
                        "Referenced artifact path does not exist",
                        "critical",
                        rel,
                        f"MLmodel references '{raw_path}', but the path was not found.",
                        "Verify artifact packaging before deployment and ensure the model directory contains referenced files.",
                    ))


def _validate_docker_and_kserve(context: ScanContext, findings: list[Finding]) -> None:
    docker = _find_file(context, "Dockerfile")
    if docker:
        rel, text = docker
        if re.search(r"FROM\s+\S+:latest", text, re.I):
            findings.append(Finding(
                "DOCKER_LATEST_TAG",
                "Docker base image uses latest tag",
                "medium",
                rel,
                "latest makes deployment builds non-reproducible.",
                "Pin the base image tag to an explicit Python runtime version.",
                "requires_confirmation",
            ))
        if "WORKDIR" not in text:
            findings.append(Finding(
                "DOCKER_WORKDIR_MISSING",
                "Dockerfile has no WORKDIR",
                "low",
                rel,
                "A missing WORKDIR often causes relative artifact and app paths to resolve differently.",
                "Add WORKDIR /app and copy model/application files relative to it.",
                "insert_workdir",
            ))
    for rel, text in context.text.items():
        if Path(rel).name in {"kserve.yaml", "kserve.yml", "serving.yaml", "serving.yml", "deployment.yaml", "deployment.yml"}:
            if "storageUri" not in text and "storageURI" not in text:
                findings.append(Finding(
                    "KSERVE_STORAGE_URI_MISSING",
                    "KServe storageUri is missing",
                    "high",
                    rel,
                    "KServe InferenceService does not declare where the model artifact is stored.",
                    "Set predictor.model.storageUri to an artifact location reachable by the serving cluster.",
                    "requires_confirmation",
                ))
            if re.search(r"storageUri:\s*['\"]?(/|file:|[A-Za-z]:)", text):
                findings.append(Finding(
                    "KSERVE_LOCAL_STORAGE_URI",
                    "KServe storageUri uses a local path",
                    "critical",
                    rel,
                    "Local paths are not portable across Kubernetes nodes.",
                    "Use object storage or PVC-backed paths approved for the serving cluster.",
                    "requires_confirmation",
                ))


def _extract_uri_values(context: ScanContext) -> list[tuple[str, str, str]]:
    values: list[tuple[str, str, str]] = []
    for rel, text in context.text.items():
        for key in ("model_uri", "MODEL_URI", "storageUri", "storageURI"):
            pattern = rf"{re.escape(key)}\s*[:=]\s*['\"]?([^\n'\" ]+)"
            for match in re.finditer(pattern, text):
                values.append((rel, key, match.group(1).strip()))
    return values


def _validate_policy(context: ScanContext, findings: list[Finding], policy: Policy) -> None:
    if not policy:
        return

    present_names = {Path(rel).name for rel in context.files}
    for required_file in policy.get("required_files", []):
        if required_file not in present_names:
            findings.append(Finding(
                "POLICY_REQUIRED_FILE_MISSING",
                "Required policy file is missing",
                "high",
                required_file,
                f"KakaoPay policy requires {required_file}, but it was not found.",
                "Add the required file or document the approved managed-runtime exception.",
                "requires_confirmation",
            ))

    approved_python = set(policy.get("approved_python_versions", []))
    if approved_python:
        for rel, version in _python_versions(context).items():
            normalized = re.search(r"[0-9]+(?:\.[0-9]+)?", version)
            if normalized and normalized.group(0) not in approved_python:
                findings.append(Finding(
                    "POLICY_PYTHON_VERSION_NOT_APPROVED",
                    "Python version is not approved by policy",
                    "high",
                    rel,
                    f"{rel} uses Python {normalized.group(0)}, but approved versions are {sorted(approved_python)}.",
                    "Align the serving runtime with the approved platform Python version.",
                    "requires_confirmation",
                ))

    for key in policy.get("required_env_keys", []):
        if key == "MLFLOW_TRACKING_URI":
            continue
        if not _has_env_key(context, key):
            findings.append(Finding(
                "POLICY_REQUIRED_ENV_MISSING",
                "Required policy environment key is missing",
                "high",
                ".env.example",
                f"KakaoPay policy requires {key} to be declared in env or config files.",
                "Declare the key with a placeholder value and keep real values in the approved secret manager.",
                "create_env_example" if key == "MLFLOW_TRACKING_URI" else "requires_confirmation",
            ))

    blocked_prefixes = tuple(policy.get("blocked_uri_prefixes", []))
    if blocked_prefixes:
        for rel, key, value in _extract_uri_values(context):
            if value.startswith(blocked_prefixes):
                findings.append(Finding(
                    "POLICY_BLOCKED_URI_PREFIX",
                    "URI is blocked by deployment policy",
                    "critical",
                    rel,
                    f"{key} uses '{value}', which matches a blocked local or non-portable URI prefix.",
                    "Use a registry or object-storage URI reachable from the serving cluster.",
                    "requires_confirmation",
                ))


def validate_project(root: str | Path, policy_path: str | Path | None = None) -> ScanReport:
    context = scan_project(root)
    policy = load_policy(policy_path)
    findings: list[Finding] = []
    _add_missing_core_files(context, findings)
    _validate_python(context, findings)
    _validate_requirements(context, findings)
    _validate_uris_and_paths(context, findings)
    _validate_docker_and_kserve(context, findings)
    _validate_policy(context, findings, policy)

    penalty = sum(SEVERITY_SCORE.get(item.severity, 0) for item in findings)
    score = max(0, 100 - penalty)
    if score < 50:
        risk_level = "blocked"
    elif score < 75:
        risk_level = "high"
    elif score < 90:
        risk_level = "medium"
    else:
        risk_level = "low"
    summary = {severity: 0 for severity in SEVERITY_SCORE}
    for finding in findings:
        summary[finding.severity] = summary.get(finding.severity, 0) + 1
    return ScanReport(
        project=str(Path(root).expanduser().resolve()),
        score=score,
        risk_level=risk_level,
        files_scanned=sorted(context.files),
        findings=findings,
        summary=summary,
    )
