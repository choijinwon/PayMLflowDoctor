import unittest

from paymlflow_doctor.validators import validate_project


class ValidatorTest(unittest.TestCase):
    def test_broken_project_is_blocked(self):
        report = validate_project("sample-data/broken-mlflow-project")
        self.assertEqual(report.risk_level, "blocked")
        self.assertTrue(any(finding.id == "PYTHON_VERSION_MISMATCH" for finding in report.findings))
        self.assertTrue(any(finding.id == "KSERVE_LOCAL_STORAGE_URI" for finding in report.findings))
        self.assertTrue(any(finding.id == "ARTIFACT_PATH_MISSING" for finding in report.findings))

    def test_healthy_project_has_no_blockers(self):
        report = validate_project("sample-data/healthy-mlflow-project")
        self.assertGreaterEqual(report.score, 90)
        self.assertFalse(any(finding.severity in {"critical", "high"} for finding in report.findings))

    def test_policy_pack_flags_broken_project(self):
        report = validate_project("sample-data/broken-mlflow-project", "policies/kakaopay-mlops-policy.yaml")
        self.assertTrue(any(finding.id == "POLICY_PYTHON_VERSION_NOT_APPROVED" for finding in report.findings))
        self.assertTrue(any(finding.id == "POLICY_BLOCKED_URI_PREFIX" for finding in report.findings))

    def test_policy_pack_allows_healthy_project(self):
        report = validate_project("sample-data/healthy-mlflow-project", "policies/kakaopay-mlops-policy.yaml")
        self.assertFalse(any(finding.id.startswith("POLICY_") for finding in report.findings))


if __name__ == "__main__":
    unittest.main()
