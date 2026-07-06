---
name: pay-mlflow-doctor
description: Validate MLflow project environments, deployment files, model URIs, artifact paths, Dockerfiles, and KServe manifests before production release.
---

# PayMLflow Doctor

Use this skill when the user asks to validate, fix, or explain MLflow deployment readiness for a project, especially for financial AI services such as FDS, recommendation, OCR, fraud detection, or model serving.

## Core Behavior

When invoked, act as a deployment copilot:

1. Identify the project or model directory.
2. Run the local validator:

```bash
python -m paymlflow_doctor.cli validate <project-path> --policy policies/kakaopay-mlops-policy.yaml --format markdown
```

3. Summarize risk in business terms:
   - `blocked`: likely deployment failure
   - `high`: release should wait for fixes
   - `medium`: release can proceed only with owner approval
   - `low`: monitor or clean up
4. Suggest concrete fixes with exact files.
5. Apply only low-risk automatic fixes when the user asks for fix mode:

```bash
python -m paymlflow_doctor.cli fix <project-path> --policy policies/kakaopay-mlops-policy.yaml --apply
```

Do not invent a complex ML model. This plugin is intentionally a rule-engine based deployment safety copilot.

## Enterprise Policy Pack

When `policies/kakaopay-mlops-policy.yaml` exists, use it as the default policy file. Treat policy findings as release-governance findings, not just lint findings. Explain them in terms of reproducibility, auditability, and safe financial AI deployment.

## User Commands

### Validate MLflow Project

Trigger phrases:

- "Validate MLflow Project"
- "MLflow 배포 전 검사해줘"
- "PayMLflow Doctor로 이 프로젝트 봐줘"

Prompt:

```text
Scan the target MLflow project for deployment-blocking environment risks. Inspect requirements.txt, conda.yaml, pyproject.toml, Dockerfile, MLmodel, config files, .env files, KServe manifests, model URIs, and artifact paths. Return a readiness score, severity-ranked findings, and release recommendation.
```

Also check for hardcoded IDs, passwords, tokens, API keys, and credential-like values. Never print the actual credential value in the report.

### Fix Environment

Trigger phrases:

- "Fix Environment"
- "안전한 자동 수정 적용해줘"
- "배포 환경 오류 고쳐줘"

Prompt:

```text
Plan safe configuration fixes first. Apply only low-risk non-secret file creation or formatting changes. For Python version alignment, dependency pinning, model URI replacement, and KServe storage changes, show a diff and ask for explicit confirmation.
```

### Generate Requirements

Prompt:

```text
Generate a minimal serving requirements.txt proposal from MLmodel, pyproject.toml, conda.yaml, and import hints. Mark the result as a proposal unless dependency versions are already pinned in the source files.
```

### Check Artifact

Prompt:

```text
Verify every artifact path referenced by MLmodel and deployment config exists in the project or is a remote URI. Flag local-only or missing paths as deployment blockers.
```

### Check Model URI

Prompt:

```text
Inspect model_uri, storageUri, runs:/, models:/, file:, s3://, gs://, and local paths. Explain whether the serving cluster can resolve the URI. Flag Windows paths and local file URIs.
```

### Check Deployment

Prompt:

```text
Inspect Dockerfile and KServe or Kubernetes serving manifests. Flag missing storageUri, local storageUri, latest base images, Python mismatch, missing WORKDIR, and missing MLflow tracking configuration.
```

## Output Format

Always prefer this response shape:

```text
Deployment readiness: <score>/100, <risk_level>

Top blockers:
1. <finding> in <file>
2. <finding> in <file>

Recommended next action:
<specific action>
```

## Auto-Fix Policy

Safe automatic fixes:

- Create `.env.example` with placeholder keys.
- Write reports to `logs/`.
- Add generated documentation files.

Requires user confirmation:

- Pin or change package versions.
- Change Python runtime version.
- Rewrite Dockerfile.
- Replace model URI or KServe storage URI.
- Normalize paths in source config.

Do not auto-fix:

- Secrets.
- Real IDs, passwords, tokens, API keys, or credential values.
- Production endpoint values.
- Registry credentials.
- Object storage permissions.
- Cluster RBAC.
