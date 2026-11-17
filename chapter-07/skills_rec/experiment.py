from __future__ import annotations

from dataclasses import asdict
from typing import Dict, List

from .config import EXPERIMENT_ID, RUNS_PER_VARIANT_PER_WORKLOAD, WORKLOADS
from .metrics import run_single_variant


def run_full_experiment() -> (List[Dict], str):
    """Run all workloads for both baseline and treatment.

    Returns a tuple: (runs, notes) where `runs` is a list of dicts
    conforming to the evidence schema, and `notes` is a human-readable
    string with non-metric information.
    """

    runs: List[Dict] = []

    for workload in WORKLOADS:
        workload_id = workload["workload_id"]
        item_type = workload["item_type"]
        n_employees = workload["n_employees"]
        n_items = workload["n_items"]

        for variant in ("baseline", "treatment"):
            for _ in range(RUNS_PER_VARIANT_PER_WORKLOAD):
                result = run_single_variant(
                    workload_id=workload_id,
                    item_type=item_type,
                    n_employees=n_employees,
                    n_items=n_items,
                    variant=variant,
                )
                metrics_dict = {
                    "engagement_rate": float(result.metrics.engagement_rate),
                    "avg_score": float(result.metrics.avg_score),
                    "n_employees": int(result.metrics.n_employees),
                    "n_items": int(result.metrics.n_items),
                }

                run_entry: Dict = {
                    "variant": result.variant,
                    "workload_id": result.workload_id,
                    "run_id": result.run_id,
                    "success": True,
                    "metrics": metrics_dict,
                    "experiment_id": EXPERIMENT_ID,
                }
                runs.append(run_entry)

    notes = (
        "Synthetic experiment for Chapter 7 skills recommendations. "
        "Metrics are simulated engagement/score measures on deterministic "
        "synthetic data; real-world CTR, completion, fairness, and A/B test "
        "statistics are not computed in this offline sandbox."
    )

    return runs, notes
