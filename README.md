# PayMLflow Doctor

MLflow Environment Validator & Deployment Copilot for financial AI deployment.

PayMLflow Doctor is a Codex Plugin and Python rule engine that catches MLflow, Docker, KServe, Python, URI, and artifact configuration risks before a model is released. It is built for the KakaoPay AX Hackathon as a practical MLOps safety copilot for FDS, recommendation, OCR, anomaly detection, and other financial AI services.

## Quick Demo

```bash
cd pay-mlflow-doctor
python -m paymlflow_doctor.cli validate sample-data/broken-mlflow-project \
  --policy policies/kakaopay-mlops-policy.yaml \
  --format markdown
```

Or run the full demo:

```bash
cd pay-mlflow-doctor
./scripts/demo.sh
```

## What It Finds

- Python version mismatch across `conda.yaml`, `Dockerfile`, `MLmodel`, and `pyproject.toml`
- Missing `MLFLOW_TRACKING_URI`
- Local `file:` model URIs
- Windows paths that break Linux containers
- Missing MLflow artifact paths
- Unsafe KServe local `storageUri`
- Unpinned Python dependencies
- Hardcoded ID, password, token, API key detection with value masking
- Enterprise policy violations from `policies/kakaopay-mlops-policy.yaml`

## Repository Layout

```text
pay-mlflow-doctor/
├── .codex-plugin/plugin.json
├── skills/pay-mlflow-doctor/SKILL.md
├── paymlflow_doctor/
├── policies/kakaopay-mlops-policy.yaml
├── sample-data/
├── scripts/demo.sh
├── tests/
└── README.md
```

The detailed architecture, hackathon scoring, MVP scope, expected Q&A, and five-minute pitch script are in [pay-mlflow-doctor/README.md](pay-mlflow-doctor/README.md).

## Submission

The generated hackathon package is included as [submission.zip](submission.zip). Rebuild it with:

```bash
cd pay-mlflow-doctor
python scripts/create_submission_zip.py
```

## Verification

```bash
cd pay-mlflow-doctor
python -m unittest discover -s tests -v
python -m paymlflow_doctor.cli validate sample-data/healthy-mlflow-project \
  --policy policies/kakaopay-mlops-policy.yaml \
  --fail-on high
```
