import json
import os
import unittest
from pathlib import Path

from experiment.config import CHAPTER_NUMBER, EXPERIMENT_ID, WORKLOAD_IDS
from experiment.simulate import run_full_experiment


class TestExperimentEvidence(unittest.TestCase):
    def setUp(self) -> None:
        # Prepare a temporary evidence directory
        self.evidence_dir = Path("/evidence")
        self.evidence_dir.mkdir(parents=True, exist_ok=True)
        self.results_file = self.evidence_dir / "results.json"

        # Generate evidence in-memory and also write it to disk to mimic run.py
        environment = {"os": "test-os", "python": "3.11.0"}
        evidence = run_full_experiment(environment=environment)
        with self.results_file.open("w", encoding="utf-8") as f:
            json.dump(evidence, f)

    def test_results_file_exists_and_is_json(self) -> None:
        self.assertTrue(self.results_file.exists(), "results.json must exist")
        with self.results_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, dict)

    def test_top_level_schema(self) -> None:
        with self.results_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Required top-level fields
        self.assertIn("chapter", data)
        self.assertIn("experiment_id", data)
        self.assertIn("environment", data)
        self.assertIn("runs", data)

        self.assertEqual(data["chapter"], CHAPTER_NUMBER)
        self.assertEqual(data["experiment_id"], EXPERIMENT_ID)

        env = data["environment"]
        self.assertIsInstance(env, dict)
        self.assertIn("os", env)
        self.assertIn("python", env)
        self.assertIsInstance(env["os"], str)
        self.assertIsInstance(env["python"], str)

        runs = data["runs"]
        self.assertIsInstance(runs, list)
        self.assertGreater(len(runs), 0)

    def test_runs_and_metrics_schema(self) -> None:
        with self.results_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
        runs = data["runs"]

        seen = {(w, v): 0 for w in WORKLOAD_IDS for v in ("baseline", "treatment")}

        for run in runs:
            # Basic keys
            self.assertIn("variant", run)
            self.assertIn("workload_id", run)
            self.assertIn("run_id", run)
            self.assertIn("success", run)
            self.assertIn("metrics", run)

            variant = run["variant"]
            workload_id = run["workload_id"]
            run_id = run["run_id"]
            success = run["success"]
            metrics = run["metrics"]

            self.assertIn(variant, ("baseline", "treatment"))
            self.assertIn(workload_id, WORKLOAD_IDS)
            self.assertIsInstance(run_id, str)
            self.assertIsInstance(success, bool)
            self.assertIsInstance(metrics, dict)

            # At least one metric and all numeric
            self.assertGreater(len(metrics), 0)
            for key, value in metrics.items():
                # Metrics must be finite JSON numbers, not bools, strings, etc.
                self.assertIsInstance(
                    value,
                    (int, float),
                    msg=f"Metric {key} must be numeric, got {type(value)}",
                )

            seen[(workload_id, variant)] += 1

        # Ensure at least one baseline and one treatment run per workload
        for workload_id in WORKLOAD_IDS:
            self.assertGreater(
                seen[(workload_id, "baseline")],
                0,
                msg=f"No baseline run for workload {workload_id}",
            )
            self.assertGreater(
                seen[(workload_id, "treatment")],
                0,
                msg=f"No treatment run for workload {workload_id}",
            )


if __name__ == "__main__":
    unittest.main()
