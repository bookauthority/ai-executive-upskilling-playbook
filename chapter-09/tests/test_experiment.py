import json
import os
import runpy
import unittest
from pathlib import Path


class TestExperimentEvidenceSchema(unittest.TestCase):
    def setUp(self) -> None:
        # Use a temporary evidence directory under the test directory so that
        # we do not rely on /evidence being writable in all environments.
        self.test_evidence_dir = Path("./.test_evidence")
        if self.test_evidence_dir.exists():
            # Clean up any pre-existing file
            results = self.test_evidence_dir / "results.json"
            if results.exists():
                results.unlink()
        else:
            self.test_evidence_dir.mkdir(parents=True, exist_ok=True)
        os.environ["BOOKMAS_EVIDENCE_DIR"] = str(self.test_evidence_dir)

    def tearDown(self) -> None:
        # Clean evidence dir after tests
        results = self.test_evidence_dir / "results.json"
        if results.exists():
            results.unlink()

    def test_run_produces_valid_evidence_file(self) -> None:
        # Execute run.py in-process
        runpy.run_path("run.py", run_name="__main__")

        results_path = self.test_evidence_dir / "results.json"
        self.assertTrue(results_path.exists(), "results.json must exist after run.py execution")

        with results_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Root keys and types
        self.assertIsInstance(data.get("chapter"), int)
        self.assertEqual(data["chapter"], 9)
        self.assertIsInstance(data.get("experiment_id"), str)
        self.assertEqual(data["experiment_id"], "exp-09-exec-ai-upskilling-measurement-framework-v1")
        self.assertIn("environment", data)
        self.assertIsInstance(data["environment"], dict)
        self.assertIn("os", data["environment"])
        self.assertIn("python", data["environment"])

        # Runs structure
        runs = data.get("runs")
        self.assertIsInstance(runs, list)
        self.assertGreaterEqual(len(runs), 6, "Expect at least 6 runs (baseline+treatment for 3 workloads)")

        # Track presence of baseline/treatment per workload
        seen = {}

        for run in runs:
            # Required fields
            self.assertIn("variant", run)
            self.assertIn("workload_id", run)
            self.assertIn("run_id", run)
            self.assertIn("success", run)
            self.assertIn("metrics", run)

            self.assertIn(run["variant"], ["baseline", "treatment"])
            self.assertIsInstance(run["workload_id"], str)
            self.assertIsInstance(run["run_id"], str)
            self.assertIsInstance(run["success"], bool)

            metrics = run["metrics"]
            self.assertIsInstance(metrics, dict)
            self.assertGreater(len(metrics), 0)
            for m_name, m_val in metrics.items():
                # Metrics must be finite numbers
                self.assertIsInstance(m_val, (int, float), f"Metric {m_name} must be numeric")

            wid = run["workload_id"]
            seen.setdefault(wid, {"baseline": 0, "treatment": 0})
            seen[wid][run["variant"]] += 1

        # Ensure each workload has at least one baseline and one treatment run
        for wid, counts in seen.items():
            self.assertGreaterEqual(
                counts["baseline"], 1, f"Workload {wid} must have at least one baseline run"
            )
            self.assertGreaterEqual(
                counts["treatment"], 1, f"Workload {wid} must have at least one treatment run"
            )

        # Notes field is optional but should exist and be a string in this implementation
        self.assertIn("notes", data)
        self.assertIsInstance(data["notes"], str)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
