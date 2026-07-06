# PayMLflow Doctor Report

## Deployment Summary

| Item | Value |
| --- | --- |
| Project | `/Users/choijinwon/Documents/Codex/2026-07-07-role-openai-codex-plugin-architect-mlops/pay-mlflow-doctor/sample-data/broken-mlflow-project` |
| Deployment Readiness Score | `0/100` |
| Risk Level | `blocked` |
| Files Scanned | `7` |
| Release Decision | Stop deployment |

## Severity Summary

| Severity | Count | Meaning |
| --- | ---: | --- |
| Critical | 4 | Deployment likely fails or violates release safety. |
| High | 6 | Must be fixed before production deployment. |
| Medium | 3 | Operational risk exists and needs owner review. |
| Low | 1 | Cleanup or hardening recommended. |
| Info | 0 | Informational context. |

## Findings

| No | Severity | Check ID | File | Finding | Recommendation | Auto Fix |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | high | `PYTHON_VERSION_MISMATCH` | `conda.yaml, Dockerfile, MLmodel` | Detected inconsistent Python versions: {'conda.yaml': '3.9', 'Dockerfile': '3.11', 'MLmodel': '3.9'}. | Choose one serving Python version and align conda.yaml, Dockerfile, MLmodel, and pyproject.toml. | Requires confirmation |
| 2 | medium | `UNPINNED_DEPENDENCIES` | `requirements.txt` | Unpinned packages detected: mlflow, pandas, numpy. | Pin production serving dependencies to exact versions for reproducible financial AI deployment. | Requires confirmation |
| 3 | medium | `IMPORT_NOT_DECLARED` | `model_code.py` | Python code imports 'xgboost', but 'xgboost' is not declared in requirements.txt. | Add the serving dependency to requirements.txt or remove the unused import before deployment. | Requires confirmation |
| 4 | high | `TRACKING_URI_MISSING` | `.env.example` | The MLflow tracking endpoint is not visible in env/config files. | Add MLFLOW_TRACKING_URI to .env.example and deployment secret documentation. | Safe |
| 5 | high | `LOCAL_MODEL_URI` | `config.yaml` | Local file model_uri values usually fail after containerization or KServe deployment. | Use models:/, runs:/, s3://, gs://, or a platform artifact URI reachable from the serving cluster. | Requires confirmation |
| 6 | medium | `WINDOWS_PATH_IN_CONFIG` | `config.yaml` | Backslash paths can break in Linux containers and Kubernetes pods. | Use POSIX-style paths or URI schemes for cross-platform deployment. | normalize_paths |
| 7 | critical | `ARTIFACT_PATH_MISSING` | `MLmodel` | MLmodel references 'missing-model.pkl', but the path was not found. | Verify artifact packaging before deployment and ensure the model directory contains referenced files. | No |
| 8 | low | `DOCKER_WORKDIR_MISSING` | `Dockerfile` | A missing WORKDIR often causes relative artifact and app paths to resolve differently. | Add WORKDIR /app and copy model/application files relative to it. | insert_workdir |
| 9 | critical | `KSERVE_LOCAL_STORAGE_URI` | `kserve.yaml` | Local paths are not portable across Kubernetes nodes. | Use object storage or PVC-backed paths approved for the serving cluster. | Requires confirmation |
| 10 | high | `POLICY_PYTHON_VERSION_NOT_APPROVED` | `conda.yaml` | conda.yaml uses Python 3.9, but approved versions are ['3.11']. | Align the serving runtime with the approved platform Python version. | Requires confirmation |
| 11 | high | `POLICY_PYTHON_VERSION_NOT_APPROVED` | `MLmodel` | MLmodel uses Python 3.9, but approved versions are ['3.11']. | Align the serving runtime with the approved platform Python version. | Requires confirmation |
| 12 | high | `POLICY_REQUIRED_ENV_MISSING` | `.env.example` | KakaoPay policy requires MODEL_URI to be declared in env or config files. | Declare the key with a placeholder value and keep real values in the approved secret manager. | Requires confirmation |
| 13 | critical | `POLICY_BLOCKED_URI_PREFIX` | `config.yaml` | model_uri uses 'file:C:\Users\pay\model', which matches a blocked local or non-portable URI prefix. | Use a registry or object-storage URI reachable from the serving cluster. | Requires confirmation |
| 14 | critical | `POLICY_BLOCKED_URI_PREFIX` | `kserve.yaml` | storageUri uses 'file:/models/fds-risk-model', which matches a blocked local or non-portable URI prefix. | Use a registry or object-storage URI reachable from the serving cluster. | Requires confirmation |

## Fix Plan

| Priority | Action | Risk |
| ---: | --- | --- |
| 1 | Choose one serving Python version and align conda.yaml, Dockerfile, MLmodel, and pyproject.toml. | high |
| 2 | Pin production serving dependencies to exact versions for reproducible financial AI deployment. | medium |
| 3 | Add the serving dependency to requirements.txt or remove the unused import before deployment. | medium |
| 4 | Add MLFLOW_TRACKING_URI to .env.example and deployment secret documentation. | high |
| 5 | Use models:/, runs:/, s3://, gs://, or a platform artifact URI reachable from the serving cluster. | high |
| 6 | Use POSIX-style paths or URI schemes for cross-platform deployment. | medium |
| 7 | Verify artifact packaging before deployment and ensure the model directory contains referenced files. | critical |
| 8 | Use object storage or PVC-backed paths approved for the serving cluster. | critical |
| 9 | Align the serving runtime with the approved platform Python version. | high |
| 10 | Align the serving runtime with the approved platform Python version. | high |
| 11 | Declare the key with a placeholder value and keep real values in the approved secret manager. | high |
| 12 | Use a registry or object-storage URI reachable from the serving cluster. | critical |
| 13 | Use a registry or object-storage URI reachable from the serving cluster. | critical |
