from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List


@dataclass
class LearnerOutcome:
    """Synthetic outcome for a single learner in a workload.

    Attributes
    ----------
    completed_pathway: bool
        Whether the learner completed at least one upskilling pathway.
    skill_gain: float
        Increase in skill score between baseline and end of measurement.
    performance_index: float
        Normalized performance index between 0 and 1.
    """

    completed_pathway: bool
    skill_gain: float
    performance_index: float


class DeterministicRandom:
    """Deterministic random number helper.

    We avoid using the global random state directly so that each workload can
    be seeded independently and reproducibly.
    """

    def __init__(self, seed: int) -> None:
        self._rng = random.Random(seed)

    def bernoulli(self, p: float) -> bool:
        return self._rng.random() < p

    def normal(self, mean: float, stddev: float) -> float:
        # Box-Muller using underlying RNG for deterministic output
        u1 = max(self._rng.random(), 1e-12)
        u2 = self._rng.random()
        z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return mean + stddev * z0

    def uniform(self, a: float, b: float) -> float:
        return self._rng.uniform(a, b)


def generate_learner_outcomes(
    n_learners: int,
    completion_rate: float,
    avg_skill_gain: float,
    skill_gain_std: float,
    base_performance_mean: float,
    performance_lift_from_skill: float,
    rng: DeterministicRandom,
) -> List[LearnerOutcome]:
    """Generate synthetic learner outcomes for a workload arm.

    Parameters are chosen to loosely resemble realistic patterns, but the
    absolute magnitudes are not meant to represent any specific organization.
    """

    outcomes: List[LearnerOutcome] = []
    for _ in range(n_learners):
        completed = rng.bernoulli(completion_rate)
        # Learners who complete tend to gain more skill.
        mean_gain = avg_skill_gain * (1.1 if completed else 0.7)
        gain = max(0.0, rng.normal(mean_gain, skill_gain_std))
        # Performance index is a bounded transformation of a latent score
        latent = base_performance_mean + performance_lift_from_skill * (gain / 10.0)
        # Add some noise and squash to [0, 1]
        latent += rng.normal(0.0, 0.1)
        perf = 1.0 / (1.0 + math.exp(-latent))
        # Rescale to [0, 1] roughly by centering typical latent range
        perf = max(0.0, min(1.0, perf))
        outcomes.append(LearnerOutcome(completed, gain, perf))
    return outcomes


def generate_cohort_trajectories(
    n_learners: int,
    months: int,
    initial_skill_mean: float,
    monthly_gain_mean: float,
    monthly_gain_std: float,
    rng: DeterministicRandom,
) -> List[List[float]]:
    """Generate monthly skill profiles for each learner in a cohort.

    Returns a list of learners, each with a list of skill levels over time.
    """

    trajectories: List[List[float]] = []
    for _ in range(n_learners):
        skill = max(0.0, rng.normal(initial_skill_mean, 5.0))
        learner_traj: List[float] = [skill]
        for _m in range(1, months):
            delta = max(0.0, rng.normal(monthly_gain_mean, monthly_gain_std))
            skill = min(100.0, skill + delta)
            learner_traj.append(skill)
        trajectories.append(learner_traj)
    return trajectories
