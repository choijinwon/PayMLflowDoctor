# PayMLflow Doctor

MLflow Environment Validator & Deployment Copilot

PayMLflow Doctor는 금융 AI 모델이 배포 직전에 실패하는 환경설정 문제를 Codex Plugin과 Python rule engine으로 사전에 탐지하는 도구입니다. 목표는 단순 환경 검사기가 아니라, 카카오페이의 FDS, 추천, OCR, 이상거래 탐지, 금융 AI 모델 배포를 더 안전하게 만드는 AI Copilot입니다.

기본 분석 보고서는 발표, PR 리뷰, 배포 승인에 바로 붙일 수 있는 Markdown table report 형태로 생성됩니다.

## 1. 해커톤 우승 가능성 평가

| 항목 | 점수 | 평가 |
| --- | ---: | --- |
| 독창성 | 8/10 | MLflow 자체 검사는 흔하지만 Codex Plugin이 배포 전 환경, URI, KServe, Docker까지 묶어 설명하고 수정 제안하는 형태는 차별점이 있습니다. |
| 사업성 | 9/10 | 금융 AI 운영에서 배포 실패, 장애, 재작업 비용을 줄이는 직접적인 ROI가 있습니다. |
| 기술성 | 8/10 | 복잡한 모델 없이도 MLflow, Docker, KServe, Python 환경 규칙을 정적 분석하는 현실적인 MLOps 기술입니다. |
| 구현 난이도 | 8/10 | 6시간 MVP 기준으로 rule engine은 가능하고, MCP 서버나 대규모 UI를 제외하면 완성도가 나옵니다. 점수는 "적절히 어려우나 완성 가능"의 의미입니다. |
| MVP 가능성 | 9/10 | 샘플 프로젝트, CLI, Codex Skill, 리포트까지 빠르게 시연 가능합니다. |
| Codex 적합성 | 10/10 | Codex가 파일을 읽고, CLI를 실행하고, 위험을 설명하고, 안전한 수정 제안을 하는 흐름과 정확히 맞습니다. |
| 카카오페이 적합성 | 9/10 | 금융 서비스는 재현성, 감사 가능성, 배포 안정성이 중요하므로 실제 도입 논리가 강합니다. |

종합: 61/70. 우승 가능성이 있는 주제입니다. 핵심 발표 메시지는 "모델 성능이 아니라 배포 환경 실패를 줄이는 금융 AI 안전장치"입니다.

## 2. 3일, 총 6시간 MVP 범위

필수 기능:

- MLflow 프로젝트 파일 스캔
- `requirements.txt`, `conda.yaml`, `pyproject.toml`, `Dockerfile`, `MLmodel`, `.env.example`, `kserve.yaml` 분석
- 모델 Python 코드의 `import`와 `requirements.txt` 선언 일치성 검사
- 현재 사용자 Python 환경의 설치 패키지 목록과 requirements 비교 옵션
- Python version mismatch 탐지
- MLflow tracking URI 누락 탐지
- artifact path 누락 탐지
- local model URI, Windows path, KServe local storageUri 탐지
- 하드코딩된 ID, password, token, API key 탐지 및 값 마스킹
- severity, score, risk level 리포트
- Codex Skill 프롬프트 제공

선택 기능:

- `.env.example` 안전 생성
- Markdown/JSON 리포트 저장
- `--fail-on high` 같은 CI gate 모드
- healthy/broken 샘플 데이터 제공
- `--policy policies/kakaopay-mlops-policy.yaml` 기반 기업 정책 검사
- `--check-python-env` 기반 현재 사용자 Python 환경 검사

확장 기능:

- 사내 MLflow registry 정책 연동
- KServe cluster dry-run
- Docker build smoke test
- 사내 승인 dependency catalog 연동
- MCP server로 검사 결과를 Codex tool call 형태로 노출

발표용 기능:

- 깨진 샘플 프로젝트 검사
- blocked 리포트 출력
- 안전 fix plan 출력
- `.env.example` 자동 생성 시연
- healthy 샘플에서 score 90점 이상 확인

## 3. Plugin 제출 구조

```text
submission.zip
└── pay-mlflow-doctor/
    ├── .codex-plugin/
    │   └── plugin.json
    ├── skills/
    │   └── pay-mlflow-doctor/
    │       └── SKILL.md
    ├── paymlflow_doctor/
    │   ├── __init__.py
    │   ├── autofix.py
    │   ├── cli.py
    │   ├── models.py
    │   ├── report.py
    │   ├── scanner.py
    │   └── validators.py
    ├── sample-data/
    │   ├── broken-mlflow-project/
    │   └── healthy-mlflow-project/
    ├── logs/
    ├── policies/
    │   └── kakaopay-mlops-policy.yaml
    ├── scripts/
    │   ├── demo.sh
    │   └── create_submission_zip.py
    ├── tests/
    │   └── test_validator.py
    ├── pyproject.toml
    └── README.md
```

`.mcp.json` 필요 여부: MVP에서는 불필요합니다. 이유는 Codex Skill이 로컬 Python CLI를 실행하는 구조만으로 6시간 내 완성 가능한 시연과 제출이 가능하기 때문입니다. 확장 단계에서는 MCP 서버를 추가해 `validate_project`, `plan_fix`, `write_report`를 tool로 노출할 수 있습니다.

## 4. Plugin 실행 흐름

```text
사용자
↓
Codex
↓
PayMLflow Doctor Skill
↓
MLflow Project Scan
↓
Environment Validation
↓
Risk Analysis
↓
Fix Suggestion
↓
Markdown/JSON Report
↓
사용자 승인 기반 안전 수정
```

## 5. 자동 분석 대상 우선순위

1. `MLmodel`: flavor, python_version, artifact path, model data path
2. `requirements.txt`: mlflow 누락, unpinned dependency
3. `conda.yaml`: Python version, pip dependency
4. `Dockerfile`: Python runtime, latest tag, WORKDIR
5. `kserve.yaml`, `serving.yaml`, `deployment.yaml`: storageUri, local path, modelFormat
6. `.env`, `.env.example`: `MLFLOW_TRACKING_URI`, `MODEL_URI`
7. `config.yaml`, `model.yaml`: model_uri, artifact path, Windows/Linux path
8. `*.py`: 모델 코드 import 추출 후 requirements 선언 여부 확인
9. 현재 Python 환경: 설치 패키지 목록과 requirements pin 비교
10. `.env`, `config.yaml`, `Dockerfile`: password, username, token, API key 등 credential-like 값
11. `pyproject.toml`: requires-python, dependency 기준
12. artifact path: MLmodel 내부 참조 경로 실제 존재 여부
13. uri: `models:/`, `runs:/`, `file:`, `s3://`, `gs://`, Windows path

## 6. Python 프로젝트 설계

Class diagram:

```text
ScanContext
  - root: Path
  - files: dict[str, Path]
  - text: dict[str, str]

Finding
  - id
  - title
  - severity
  - file
  - message
  - recommendation
  - autofix

ScanReport
  - project
  - score
  - risk_level
  - files_scanned
  - findings
  - summary
```

Functions:

| Function | Input | Output |
| --- | --- | --- |
| `scan_project(root)` | project path | `ScanContext` |
| `validate_project(root)` | project path | `ScanReport` |
| `validate_project(root, check_python_env=True)` | project path + current Python env | `ScanReport` |
| `to_json(report)` | `ScanReport` | JSON string |
| `to_markdown(report)` | `ScanReport` | Markdown string |
| `plan_fixes(root)` | project path | fix plan list |
| `apply_safe_fixes(root)` | project path | applied action list |

JSON 예시:

```json
{
  "project": "/repo/sample-data/broken-mlflow-project",
  "score": 0,
  "risk_level": "blocked",
  "summary": {
    "critical": 2,
    "high": 3,
    "medium": 2,
    "low": 1,
    "info": 0
  },
  "findings": [
    {
      "id": "PYTHON_VERSION_MISMATCH",
      "title": "Python versions do not match",
      "severity": "high",
      "file": "conda.yaml, Dockerfile, MLmodel",
      "recommendation": "Choose one serving Python version and align all runtime files."
    }
  ]
}
```

CLI 예시:

```bash
python -m paymlflow_doctor.cli validate sample-data/broken-mlflow-project --format markdown
python -m paymlflow_doctor.cli validate sample-data/broken-mlflow-project --policy policies/kakaopay-mlops-policy.yaml
python -m paymlflow_doctor.cli validate sample-data/broken-mlflow-project --check-python-env
python -m paymlflow_doctor.cli python-env --format markdown --limit 30
python -m paymlflow_doctor.cli validate sample-data/broken-mlflow-project --format json --output logs/report.json
python -m paymlflow_doctor.cli validate sample-data/broken-mlflow-project --fail-on high
python -m paymlflow_doctor.cli fix sample-data/broken-mlflow-project --policy policies/kakaopay-mlops-policy.yaml
python -m paymlflow_doctor.cli fix sample-data/broken-mlflow-project --apply
```

## 7. Codex Skill 설계

Skill 파일: `skills/pay-mlflow-doctor/SKILL.md`

사용 예시:

- "Validate MLflow Project"
- "Fix Environment"
- "Generate Requirements"
- "Check Artifact"
- "Check Model URI"
- "Check Deployment"

핵심 Skill Prompt:

```text
Scan the target MLflow project for deployment-blocking environment risks. Inspect requirements.txt, conda.yaml, pyproject.toml, Dockerfile, MLmodel, config files, .env files, KServe manifests, model URIs, and artifact paths. Return a readiness score, severity-ranked findings, and release recommendation.
```

## 8. Auto Fix 정책

자동 수정 가능:

- `.env.example` 생성
- placeholder 환경변수 키 추가
- Markdown/JSON report 생성
- 누락된 logs 디렉터리 생성

사용자 확인 필요:

- dependency version pinning
- Python version alignment
- Dockerfile 변경
- `model_uri` 변경
- KServe `storageUri` 변경
- Windows path를 POSIX path로 변경

수정 불가:

- secret 값 추론
- 실제 ID/password/token/API key 저장 또는 출력
- 사내 endpoint 임의 생성
- object storage 권한 수정
- Kubernetes RBAC 수정
- production registry promotion

## 9. 설치와 사용법

설치:

```bash
cd pay-mlflow-doctor
python -m pip install -e .
```

검사:

```bash
paymlflow-doctor validate sample-data/broken-mlflow-project --policy policies/kakaopay-mlops-policy.yaml --format markdown
```

현재 사용자 Python 환경까지 검사:

```bash
paymlflow-doctor python-env --format markdown --limit 30
paymlflow-doctor validate sample-data/broken-mlflow-project --check-python-env
```

JSON 리포트:

```bash
paymlflow-doctor validate sample-data/broken-mlflow-project --policy policies/kakaopay-mlops-policy.yaml --format json --output logs/demo-report.json
```

안전 수정 계획:

```bash
paymlflow-doctor fix sample-data/broken-mlflow-project --policy policies/kakaopay-mlops-policy.yaml
```

발표 데모:

```bash
./scripts/demo.sh
```

VSCode에서 실행:

```text
Command Palette → Tasks: Run Task → PayMLflow Doctor: Run Demo
```

안전 수정 적용:

```bash
paymlflow-doctor fix sample-data/broken-mlflow-project --apply
```

제출 zip 생성:

```bash
python scripts/create_submission_zip.py
```

## 10. 데모 결과

Broken sample에서 기대되는 결과:

- Python 3.9와 Docker Python 3.11 mismatch
- KServe local storageUri
- Windows path 포함 model_uri
- MLflow tracking URI 누락
- MLmodel artifact path 누락
- unpinned dependency
- 모델 코드에서 import한 `xgboost`가 requirements에 없는 문제
- `--check-python-env` 사용 시 현재 Python 환경에 설치되지 않은 패키지 또는 pin mismatch

Healthy sample에서 기대되는 결과:

- score 90 이상
- critical/high blocker 없음

## 해커톤 핵심 질문 5개 답변

1. 왜 카카오페이에 필요한가?
   금융 AI는 모델 정확도만큼 배포 재현성과 장애 예방이 중요합니다. 이 도구는 배포 직전 환경 오류를 사전에 차단합니다.

2. 단순 lint와 무엇이 다른가?
   개별 파일 문법 검사가 아니라 MLflow, Docker, KServe, artifact, URI를 배포 흐름 기준으로 연결해 위험도를 판단합니다.

3. AI 모델 없이도 가치가 있는가?
   있습니다. 운영 실패의 상당수는 예측 모델 문제가 아니라 환경과 경로 문제입니다. rule engine이 더 설명 가능하고 감사 가능합니다.

4. Codex Plugin이어야 하는 이유는?
   Codex는 repo를 읽고, 명령을 실행하고, diff를 제안하고, 사용자의 승인을 받아 수정하는 개발 워크플로에 바로 들어갑니다.

5. 실제 도입 시 보안상 안전한가?
   secret-like key는 critical로 탐지하고 값은 리포트에 출력하지 않습니다. 현재 MVP는 placeholder와 정책 제안 중심이며 production 값은 자동 생성하지 않습니다.

## 예상 질문 20개

1. MLflow 버전별 차이는 어떻게 처리하나? Rule set을 버전별로 분리합니다.
2. 사내 package mirror는 어떻게 반영하나? dependency policy 파일을 추가합니다.
3. KServe가 아닌 BentoML이면? serving adapter를 추가합니다.
4. secret 노출 위험은? secret value masking rule을 추가합니다.
5. false positive는? severity와 allowlist를 둡니다.
6. CI에서 쓸 수 있나? `--fail-on high`로 gate 처리합니다.
7. 모델 성능 검증도 하나? MVP 범위 밖입니다. 배포 환경 안전성에 집중합니다.
8. Windows 개발자도 지원하나? Windows path 탐지를 지원합니다.
9. Docker build까지 하나? 확장 기능입니다.
10. cluster 접근이 필요한가? MVP는 정적 분석이라 필요 없습니다.
11. 왜 MCP를 제외했나? 6시간 MVP에서는 Skill+CLI가 더 확실합니다.
12. 자동 수정은 어디까지 하나? low-risk 파일 생성까지만 즉시 적용합니다.
13. 금융 감사에 맞나? rule 기반이라 리포트와 근거가 남습니다.
14. MLmodel이 없으면? critical blocker로 표시합니다.
15. artifact 저장소 권한은 확인하나? MVP는 URI 형식만 보고, 확장 시 live probe를 추가합니다.
16. pyproject만 있는 프로젝트는? `requires-python`을 분석합니다.
17. 모델 registry 연동은? `models:/` URI 정책으로 확장합니다.
18. 배포 실패 비용을 어떻게 줄이나? PR/CI 단계에서 조기 탐지합니다.
19. 운영팀과 개발팀 모두 쓰나? 개발자는 수정, 운영팀은 release gate로 씁니다.
20. 우승 포인트는? 카카오페이가 실제로 도입 가능한 작고 강한 MLOps 안전장치라는 점입니다.

## 5분 발표 대본

0:00-0:40 문제:
카카오페이의 금융 AI 모델은 FDS, 추천, OCR, 이상거래 탐지처럼 실제 서비스와 연결됩니다. 그런데 배포 실패는 모델 자체보다 requirements, Python version, MLflow URI, artifact path, KServe storageUri 같은 환경설정에서 자주 발생합니다.

0:40-1:20 해결:
PayMLflow Doctor는 Codex Plugin 기반 MLflow Environment Validator입니다. Codex가 프로젝트를 읽고 Python rule engine을 실행해 배포 전 위험을 점수화하고, 파일 단위로 수정 제안을 제공합니다.

1:20-2:20 데모:
깨진 샘플 프로젝트를 검사하면 Python version mismatch, local KServe storageUri, Windows model path, tracking URI 누락, artifact path 누락이 blocked로 표시됩니다. 이 결과는 Markdown과 JSON으로 남길 수 있어 CI와 리뷰에 연결됩니다.

2:20-3:20 기술:
복잡한 AI 모델은 만들지 않았습니다. Python, MLflow 파일 구조, Dockerfile, KServe manifest를 정적 분석하는 rule engine입니다. 그래서 빠르게 만들 수 있고, 설명 가능하며, 금융권 감사와 운영에 적합합니다.

3:20-4:20 Codex 적합성:
Codex는 단순히 결과를 보여주지 않습니다. 어떤 파일이 위험한지 설명하고, 안전한 자동 수정은 적용하고, 위험한 변경은 사용자 확인을 요구합니다. 이 흐름이 실제 개발자의 PR 리뷰와 배포 준비 과정에 맞습니다.

4:20-5:00 임팩트:
PayMLflow Doctor는 모델 배포 실패를 사전에 줄이는 작은 안전장치입니다. 카카오페이라면 이것을 CI gate, 모델 registry promotion, KServe 배포 전 검증 단계에 붙여 실제 운영 비용을 줄일 수 있습니다.

## 5분 발표 자료 구성

1. 제목: PayMLflow Doctor
2. 문제: 모델보다 환경설정 때문에 배포가 실패한다
3. 대상: FDS, 추천, OCR, 이상거래 탐지, 금융 AI
4. 해결: Codex Plugin + Python Rule Engine
5. 아키텍처: User → Codex → Skill → Scan → Validate → Report → Fix
6. 검사 항목: MLmodel, requirements, conda, Dockerfile, KServe, URI
7. 데모: broken project blocked report
8. 자동 수정 정책: safe / confirmation / no-fix
9. 도입 방안: PR check, CI gate, model promotion check
10. 결론: 금융 AI 배포를 안전하게 만드는 Copilot
