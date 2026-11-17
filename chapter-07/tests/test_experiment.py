import json
import os
import tempfile
import unittest

from skills_rec.config import CHAPTER_NUMBER, EXPERIMENT_ID, WORKLOADS
from skills_rec.experiment import run_full_experiment


class TestExperimentEvidenceSchema(unittest.TestCase):
    def test_run_full_experiment_structure(self):
        runs, notes = run_full_experiment()

        self.assertIsInstance(runs, list)
        self.assertIsInstance(notes, str)
        self.assertGreater(len(runs), 0)

        workload_ids = {w["workload_id"] for w in WORKLOADS}

        # Ensure we have at least one baseline and treatment per workload
        variants_by_workload = {wid: set() for wid in workload_ids}

        for run in runs:
            self.assertIn("variant", run)
            self.assertIn("workload_id", run)
            self.assertIn("run_id", run)
            self.assertIn("success", run)
            self.assertIn("metrics", run)

            self.assertIn(run["workload_id"], workload_ids)
            variants_by_workload[run["workload_id"]].add(run["variant"])

            self.assertIsInstance(run["success"], bool)
            self.assertEqual(run["experiment_id"], EXPERIMENT_ID)

            metrics = run["metrics"]
            self.assertIsInstance(metrics, dict)
            # Required metrics must be present and numeric
            for key in ["engagement_rate", "avg_score", "n_employees", "n_items"]:
                self.assertIn(key, metrics)
                val = metrics[key]
                self.assertIsInstance(val, (int, float))

        for wid, variants in variants_by_workload.items():
            self.assertIn("baseline", variants, f"Missing baseline for {wid}")
            self.assertIn("treatment", variants, f"Missing treatment for {wid}")

    def test_run_py_writes_valid_json_file(self):
        # Simulate running run.py by calling run_full_experiment and writing file
        runs, notes = run_full_experiment()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.environ["BOOKMAS_EVIDENCE_DIR"] = tmpdir
            from run import main as run_main

            run_main()
            path = os.path.join(tmpdir, "results.json")
            self.assertTrue(os.path.exists(path))

            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

        self.assertEqual(data["chapter"], CHAPTER_NUMBER)
        self.assertEqual(data["experiment_id"], EXPERIMENT_ID)
        self.assertIn("environment", data)
        self.assertIn("runs", data)
        self.assertIsInstance(data["runs"], list)

        for run in data["runs"]:
            self.assertIn("variant", run)
            self.assertIn("workload_id", run)
            self.assertIn("run_id", run)
            self.assertIn("success", run)
            self.assertIn("metrics", run)
            self.assertIsInstance(run["success"], bool)

            metrics = run["metrics"]
            self.assertIsInstance(metrics, dict)
            for key, val in metrics.items():
                # All metric values must be finite numbers
                self.assertIsInstance(val, (int, float), msg=f"Metric {key} must be numeric")


if __name__ == "__main__":
    unittest.main()
