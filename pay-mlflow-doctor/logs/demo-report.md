# PayMLflow Doctor Report

- Project: `/Users/choijinwon/Documents/Codex/2026-07-07-role-openai-codex-plugin-architect-mlops/pay-mlflow-doctor/sample-data/broken-mlflow-project`
- Deployment readiness score: `0/100`
- Risk level: `blocked`
- Files scanned: `6`

## Findings

### 1. Python versions do not match

- ID: `PYTHON_VERSION_MISMATCH`
- Severity: `high`
- File: `conda.yaml, Dockerfile, MLmodel`
- Message: Detected inconsistent Python versions: {'conda.yaml': '3.9', 'Dockerfile': '3.11', 'MLmodel': '3.9'}.
- Recommendation: Choose one serving Python version and align conda.yaml, Dockerfile, MLmodel, and pyproject.toml.
- Auto fix: `requires_confirmation`

### 2. Unpinned dependencies reduce reproducibility

- ID: `UNPINNED_DEPENDENCIES`
- Severity: `medium`
- File: `requirements.txt`
- Message: Unpinned packages detected: mlflow, pandas, numpy.
- Recommendation: Pin production serving dependencies to exact versions for reproducible financial AI deployment.
- Auto fix: `requires_confirmation`

### 3. MLFLOW_TRACKING_URI is not declared

- ID: `TRACKING_URI_MISSING`
- Severity: `high`
- File: `.env.example`
- Message: The MLflow tracking endpoint is not visible in env/config files.
- Recommendation: Add MLFLOW_TRACKING_URI to .env.example and deployment secret documentation.
- Auto fix: `create_env_example`

### 4. Model URI points to a local file path

- ID: `LOCAL_MODEL_URI`
- Severity: `high`
- File: `config.yaml`
- Message: Local file model_uri values usually fail after containerization or KServe deployment.
- Recommendation: Use models:/, runs:/, s3://, gs://, or a platform artifact URI reachable from the serving cluster.
- Auto fix: `requires_confirmation`

### 5. Windows path separator detected

- ID: `WINDOWS_PATH_IN_CONFIG`
- Severity: `medium`
- File: `config.yaml`
- Message: Backslash paths can break in Linux containers and Kubernetes pods.
- Recommendation: Use POSIX-style paths or URI schemes for cross-platform deployment.
- Auto fix: `normalize_paths`

### 6. Referenced artifact path does not exist

- ID: `ARTIFACT_PATH_MISSING`
- Severity: `critical`
- File: `MLmodel`
- Message: MLmodel references 'missing-model.pkl', but the path was not found.
- Recommendation: Verify artifact packaging before deployment and ensure the model directory contains referenced files.
- Auto fix: `none`

### 7. Dockerfile has no WORKDIR

- ID: `DOCKER_WORKDIR_MISSING`
- Severity: `low`
- File: `Dockerfile`
- Message: A missing WORKDIR often causes relative artifact and app paths to resolve differently.
- Recommendation: Add WORKDIR /app and copy model/application files relative to it.
- Auto fix: `insert_workdir`

### 8. KServe storageUri uses a local path

- ID: `KSERVE_LOCAL_STORAGE_URI`
- Severity: `critical`
- File: `kserve.yaml`
- Message: Local paths are not portable across Kubernetes nodes.
- Recommendation: Use object storage or PVC-backed paths approved for the serving cluster.
- Auto fix: `requires_confirmation`

### 9. Python version is not approved by policy

- ID: `POLICY_PYTHON_VERSION_NOT_APPROVED`
- Severity: `high`
- File: `conda.yaml`
- Message: conda.yaml uses Python 3.9, but approved versions are ['3.11'].
- Recommendation: Align the serving runtime with the approved platform Python version.
- Auto fix: `requires_confirmation`

### 10. Python version is not approved by policy

- ID: `POLICY_PYTHON_VERSION_NOT_APPROVED`
- Severity: `high`
- File: `MLmodel`
- Message: MLmodel uses Python 3.9, but approved versions are ['3.11'].
- Recommendation: Align the serving runtime with the approved platform Python version.
- Auto fix: `requires_confirmation`

### 11. Required policy environment key is missing

- ID: `POLICY_REQUIRED_ENV_MISSING`
- Severity: `high`
- File: `.env.example`
- Message: KakaoPay policy requires MODEL_URI to be declared in env or config files.
- Recommendation: Declare the key with a placeholder value and keep real values in the approved secret manager.
- Auto fix: `requires_confirmation`

### 12. URI is blocked by deployment policy

- ID: `POLICY_BLOCKED_URI_PREFIX`
- Severity: `critical`
- File: `config.yaml`
- Message: model_uri uses 'file:C:\Users\pay\model', which matches a blocked local or non-portable URI prefix.
- Recommendation: Use a registry or object-storage URI reachable from the serving cluster.
- Auto fix: `requires_confirmation`

### 13. URI is blocked by deployment policy

- ID: `POLICY_BLOCKED_URI_PREFIX`
- Severity: `critical`
- File: `kserve.yaml`
- Message: storageUri uses 'file:/models/fds-risk-model', which matches a blocked local or non-portable URI prefix.
- Recommendation: Use a registry or object-storage URI reachable from the serving cluster.
- Auto fix: `requires_confirmation`
