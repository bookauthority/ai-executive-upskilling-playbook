from __future__ import annotations

from typing import Dict, List

from .config import WORKLOAD_IDS
from .data_generation import DeterministicRandom, generate_learner_outcomes, generate_cohort_trajectories
from .metrics import summarise_outcomes


def _simulate_workload1() -> List[Dict]:
    """Simulate Workload 1: A/B learning experience experiment.

    Returns a list of run dicts (baseline and treatment) with metrics.
    """

    workload_id = WORKLOAD_IDS["workload1"]
    # Baseline arm: modest completion and skill gains
    rng_baseline = DeterministicRandom(seed=101)
    baseline_outcomes = generate_learner_outcomes(
        n_learners=400,
        completion_rate=0.6,
        avg_skill_gain=5.0,
        skill_gain_std=2.0,
        base_performance_mean=0.0,
        performance_lift_from_skill=0.15,
        rng=rng_baseline,
    )
    baseline_metrics = summarise_outcomes(baseline_outcomes)

    # Treatment arm: improved completion and skill gain, slightly higher
    # translation of skill into performance.
    rng_treatment = DeterministicRandom(seed=102)
    treatment_outcomes = generate_learner_outcomes(
        n_learners=400,
        completion_rate=0.68,
        avg_skill_gain=6.0,
        skill_gain_std=2.0,
        base_performance_mean=0.0,
        performance_lift_from_skill=0.18,
        rng=rng_treatment,
    )
    treatment_metrics = summarise_outcomes(treatment_outcomes)

    return [
        {
            "variant": "baseline",
            "workload_id": workload_id,
            "run_id": "workload1_baseline_run1",
            "success": True,
            "metrics": baseline_metrics,
        },
        {
            "variant": "treatment",
            "workload_id": workload_id,
            "run_id": "workload1_treatment_run1",
            "success": True,
            "metrics": treatment_metrics,
        },
    ]


def _simulate_workload2() -> List[Dict]:
    """Simulate Workload 2: Multi-arm recommendation algorithms.

    We map this back to the required evidence schema by reporting at least one
    baseline and one treatment run. Internally we simulate three arms but
    aggregate all non-baseline arms into a single "treatment" run for
    simplicity, using averages across arms.
    """

    workload_id = WORKLOAD_IDS["workload2"]

    # Baseline heuristic model (R0)
    rng_r0 = DeterministicRandom(seed=201)
    r0_outcomes = generate_learner_outcomes(
        n_learners=500,
        completion_rate=0.55,
        avg_skill_gain=4.5,
        skill_gain_std=1.8,
        base_performance_mean=-0.1,
        performance_lift_from_skill=0.12,
        rng=rng_r0,
    )
    baseline_metrics = summarise_outcomes(r0_outcomes)

    # Skills-graph model (R1)
    rng_r1 = DeterministicRandom(seed=202)
    r1_outcomes = generate_learner_outcomes(
        n_learners=500,
        completion_rate=0.6,
        avg_skill_gain=5.2,
        skill_gain_std=1.9,
        base_performance_mean=-0.05,
        performance_lift_from_skill=0.15,
        rng=rng_r1,
    )
    r1_metrics = summarise_outcomes(r1_outcomes)

    # Contextual bandit model (R2)
    rng_r2 = DeterministicRandom(seed=203)
    r2_outcomes = generate_learner_outcomes(
        n_learners=500,
        completion_rate=0.62,
        avg_skill_gain=5.5,
        skill_gain_std=2.0,
        base_performance_mean=-0.05,
        performance_lift_from_skill=0.17,
        rng=rng_r2,
    )
    r2_metrics = summarise_outcomes(r2_outcomes)

    # Aggregate the two treatment arms by simple averaging of metrics. This
    # preserves numeric types and represents a composite "enhanced
    # recommendation" treatment relative to the heuristic baseline.
    treatment_metrics = {}
    for key in r1_metrics.keys():
        treatment_metrics[key] = (r1_metrics[key] + r2_metrics[key]) / 2.0

    return [
        {
            "variant": "baseline",
            "workload_id": workload_id,
            "run_id": "workload2_baseline_r0",
            "success": True,
            "metrics": baseline_metrics,
        },
        {
            "variant": "treatment",
            "workload_id": workload_id,
            "run_id": "workload2_treatment_r1r2_avg",
            "success": True,
            "metrics": treatment_metrics,
        },
    ]


def _simulate_workload3() -> List[Dict]:
    """Simulate Workload 3: Cohort and longitudinal tracking.

    We model two cohorts (Q1 and Q2) with different average monthly gains and
    treat the presence of AI upskilling as a "treatment" vs. a synthetic
    matched comparison group.
    """

    workload_id = WORKLOAD_IDS["workload3"]

    # Q1 cohort with program exposure (treatment)
    rng_q1 = DeterministicRandom(seed=301)
    traj_q1 = generate_cohort_trajectories(
        n_learners=300,
        months=6,
        initial_skill_mean=50.0,
        monthly_gain_mean=3.0,
        monthly_gain_std=1.0,
        rng=rng_q1,
    )

    # Matched non-participant comparison group for Q1 (baseline)
    rng_q1_cmp = DeterministicRandom(seed=302)
    traj_q1_cmp = generate_cohort_trajectories(
        n_learners=300,
        months=6,
        initial_skill_mean=50.0,
        monthly_gain_mean=1.8,
        monthly_gain_std=0.8,
        rng=rng_q1_cmp,
    )

    # Convert trajectories into LearnerOutcome-like summaries by taking total
    # gain and mapping that to a completion and performance proxy.
    def summarise_traj(traj_list):
        from .data_generation import LearnerOutcome

        outcomes = []
        for path in traj_list:
            gain = max(0.0, path[-1] - path[0])
            completed = gain >= 8.0  # arbitrary but consistent rule
            # Performance index: more gain => better index
            perf = 1.0 / (1.0 + 2.71828 ** (-(gain / 10.0)))
            perf = max(0.0, min(1.0, perf))
            outcomes.append(LearnerOutcome(completed, gain, perf))
        return outcomes

    baseline_outcomes = summarise_traj(traj_q1_cmp)
    treatment_outcomes = summarise_traj(traj_q1)

    baseline_metrics = summarise_outcomes(baseline_outcomes)
    treatment_metrics = summarise_outcomes(treatment_outcomes)

    return [
        {
            "variant": "baseline",
            "workload_id": workload_id,
            "run_id": "workload3_cohort_q1_comparison",
            "success": True,
            "metrics": baseline_metrics,
        },
        {
            "variant": "treatment",
            "workload_id": workload_id,
            "run_id": "workload3_cohort_q1_program",
            "success": True,
            "metrics": treatment_metrics,
        },
    ]


def run_all_workloads() -> List[Dict]:
    """Run all workloads and collect run records.

    This produces a flat list of run dictionaries, each of which will be
    embedded under the `runs` field in the evidence JSON object.
    """

    runs: List[Dict] = []
    runs.extend(_simulate_workload1())
    runs.extend(_simulate_workload2())
    runs.extend(_simulate_workload3())
    return runs
