from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


def build_evidence_object(
    chapter: int,
    experiment_id: str,
    environment: Dict[str, Any],
    runs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Construct the top-level evidence object.

    Notes on additional fields:
    - `notes` provides human-readable context and limitations.
    - `simulation_details` is an extra field explicitly *not* used as a
      measurement container; all numeric metrics remain confined to the
      `metrics` mappings for each run, per the runtime contract.
    """

    notes = (
        "Synthetic, deterministic simulations of three workloads for chapter 9. "
        "Metrics are computed from generated learner outcomes: "
        "learning_pathway_completion_rate, skill_proficiency_gain, and "
        "on_job_performance_index. Metrics that cannot be meaningfully measured "
        "in this offline sandbox (e.g., program_roi, executive_dashboard_usage) "
        "are intentionally omitted from the metrics objects."
    )

    evidence: Dict[str, Any] = {
        "chapter": chapter,
        "experiment_id": experiment_id,
        "environment": environment,
        "runs": runs,
        "notes": notes,
        "simulation_details": {
            "workloads": [
                {
                    "id": r["workload_id"],
                    "variant": r["variant"],
                    "run_id": r["run_id"],
                }
                for r in runs
            ],
        },
    }
    return evidence


def write_evidence(evidence: Dict[str, Any], evidence_dir: Path) -> None:
    """Write evidence JSON to evidence_dir/results.json.

    The directory is created if it does not exist. The file is overwritten if
    present.
    """

    evidence_dir.mkdir(parents=True, exist_ok=True)
    out_path = evidence_dir / "results.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)
