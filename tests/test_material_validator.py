import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.material_validator import REQUIRED_MATERIALS, scan_materials, validate_materials


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = REPOSITORY_ROOT / "tests" / "cases"


class MaterialValidatorTests(unittest.TestCase):
    def test_missing_directory_reports_all_required_materials(self):
        result = validate_materials("path-that-does-not-exist")

        self.assertEqual(result["total_found_required"], 0)
        self.assertEqual(len(result["missing_required"]), len(REQUIRED_MATERIALS))
        self.assertEqual(result["completeness_score"], 0)

    def test_recognizes_shared_information_list(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            shared_list = Path(temp_dir, "与第三方共享个人信息清单.xlsx")
            shared_list.touch()

            found = scan_materials(temp_dir)

        self.assertEqual(found["shared_info_list"], str(shared_list))

    def test_recognizes_personalized_recommendation_material(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            recommendation = Path(temp_dir, "个性化推荐设置说明.md")
            recommendation.touch()

            found = scan_materials(temp_dir)

        self.assertEqual(found["personalized_recommendation"], str(recommendation))

    def test_ignores_hidden_and_generated_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, ".隐私政策.md").touch()
            Path(temp_dir, "_用户协议.md").touch()

            found = scan_materials(temp_dir)

        self.assertNotIn("privacy_policy", found)
        self.assertNotIn("user_agreement", found)

    def test_complete_case_is_ready_for_review(self):
        result = validate_materials(CASES_DIR / "complete")

        self.assertEqual(result["missing_required"], [])
        self.assertEqual(result["total_found_required"], len(REQUIRED_MATERIALS))
        self.assertEqual(result["completeness_score"], 80)
        expected_files = {
            "apk": "release.apk",
            "privacy_policy": "最新版隐私政策.md",
            "user_agreement": "用户服务协议.md",
            "sdk_list": "SDK清单.xlsx",
            "permission_list": "权限使用清单.xlsx",
            "business_functions": "业务功能清单.xlsx",
            "collected_info_list": "已收集个人信息清单.xlsx",
            "shared_info_list": "与第三方共享个人信息清单.xlsx",
        }
        actual_files = {
            material_id: Path(path).name
            for material_id, path in result["found_materials"].items()
            if material_id in expected_files
        }
        self.assertEqual(actual_files, expected_files)
        self.assertEqual(len(set(result["found_materials"].values())), len(result["found_materials"]))

    def test_incomplete_case_reports_six_missing_required_materials(self):
        result = validate_materials(CASES_DIR / "incomplete")

        self.assertEqual(result["total_found_required"], 2)
        self.assertEqual(len(result["missing_required"]), 6)
        self.assertEqual(result["completeness_score"], 20)

    def test_cli_writes_machine_readable_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir, "validation-report.json")
            completed = subprocess.run(
                [
                    sys.executable,
                    str(REPOSITORY_ROOT / "scripts" / "material_validator.py"),
                    "--materials-dir",
                    str(CASES_DIR / "complete"),
                    "--output",
                    str(output),
                ],
                check=False,
                capture_output=True,
            )

            report = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(report["missing_required"], [])
        self.assertEqual(report["total_found_required"], len(REQUIRED_MATERIALS))

    def test_ignores_unsupported_extension_for_required_material(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            Path(temp_dir, "隐私政策.exe").touch()

            found = scan_materials(temp_dir)

        self.assertNotIn("privacy_policy", found)


if __name__ == "__main__":
    unittest.main()
