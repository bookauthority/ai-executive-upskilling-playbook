from __future__ import annotations

import uuid
from dataclasses import asdict, dataclass
from typing import Dict, List

from .config import CHAPTER_NUMBER, EXPERIMENT_ID, USERS_PER_RUN, WORKLOAD_IDS
from .workloads import WORKLOAD_CLASS_MAP


@dataclass
class RunRecord:
    variant: str
    workload_id: str
    run_id: str
    success: bool
    metrics: Dict[str, float]


def simulate_variant_for_workload(workload_id: str, variant: str) -> RunRecord:
    workload_cls = WORKLOAD_CLASS_MAP[workload_id]
    workload = workload_cls(variant=variant, workload_id=workload_id)

    result = workload.run_simulation(num_users=USERS_PER_RUN)

    metrics = {
        "pathway_completion_rate": float(result.pathway_completion_rate),
        "avg_learning_minutes": float(result.avg_learning_minutes),
        "avg_assessment_improvement": float(result.avg_assessment_improvement),
        "weekly_active_learners_rate": float(result.weekly_active_learners_rate),
    }

    run_id = str(uuid.uuid4())
    return RunRecord(
        variant=variant,
        workload_id=workload_id,
        run_id=run_id,
        success=True,
        metrics=metrics,
    )


def run_full_experiment(environment: Dict[str, str]) -> Dict:
    runs: List[RunRecord] = []

    for workload_id in WORKLOAD_IDS:
        # Baseline
        runs.append(simulate_variant_for_workload(workload_id, "baseline"))
        # Treatment
        runs.append(simulate_variant_for_workload(workload_id, "treatment"))

    evidence = {
        "chapter": CHAPTER_NUMBER,
        "experiment_id": EXPERIMENT_ID,
        "environment": environment,
        "runs": [asdict(r) for r in runs],
        "notes": (
            "Simulated RCT for GenAI learning copilot vs. baseline using "
            "deterministic synthetic users. Metrics are synthetic but derived "
            "from actual instrumented execution within this offline sandbox."
        ),
    }

    return evidence
