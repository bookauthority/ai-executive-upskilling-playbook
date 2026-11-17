from __future__ import annotations

from typing import Iterable

from .data_generation import LearnerOutcome


def compute_learning_pathway_completion_rate(outcomes: Iterable[LearnerOutcome]) -> float:
    outcomes_list = list(outcomes)
    if not outcomes_list:
        return 0.0
    completed = sum(1 for o in outcomes_list if o.completed_pathway)
    return completed / len(outcomes_list)


def compute_skill_proficiency_gain(outcomes: Iterable[LearnerOutcome]) -> float:
    outcomes_list = list(outcomes)
    if not outcomes_list:
        return 0.0
    total_gain = sum(o.skill_gain for o in outcomes_list)
    return total_gain / len(outcomes_list)


def compute_on_job_performance_index(outcomes: Iterable[LearnerOutcome]) -> float:
    outcomes_list = list(outcomes)
    if not outcomes_list:
        return 0.0
    total = sum(o.performance_index for o in outcomes_list)
    return total / len(outcomes_list)


def summarise_outcomes(outcomes: Iterable[LearnerOutcome]) -> dict:
    """Return metrics dict computed from learner outcomes.

    The keys correspond to a subset of the chapter's metric framework that is
    feasible to simulate here.
    """

    return {
        "learning_pathway_completion_rate": compute_learning_pathway_completion_rate(outcomes),
        "skill_proficiency_gain": compute_skill_proficiency_gain(outcomes),
        "on_job_performance_index": compute_on_job_performance_index(outcomes),
    }
