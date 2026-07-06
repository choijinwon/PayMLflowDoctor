#!/usr/bin/env bash
set -euo pipefail

POLICY="policies/kakaopay-mlops-policy.yaml"

echo "== PayMLflow Doctor: broken project =="
python -m paymlflow_doctor.cli validate sample-data/broken-mlflow-project \
  --policy "$POLICY" \
  --format markdown

echo
echo "== Safe fix plan =="
python -m paymlflow_doctor.cli fix sample-data/broken-mlflow-project \
  --policy "$POLICY"

echo
echo "== PayMLflow Doctor: healthy project =="
python -m paymlflow_doctor.cli validate sample-data/healthy-mlflow-project \
  --policy "$POLICY" \
  --format markdown
