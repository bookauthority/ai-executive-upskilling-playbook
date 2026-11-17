from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, List

from .config import GLOBAL_SEED


@dataclass
class SimulationResult:
    pathway_completion_rate: float
    avg_learning_minutes: float
    avg_assessment_improvement: float
    weekly_active_learners_rate: float


class BaseWorkload:
    """Abstract workload definition providing a simulation API.

    Each concrete workload has a baseline and a treatment variant. The
    `run_simulation` method returns numeric metrics derived from synthetic
    user behavior under that variant.
    """

    def __init__(self, variant: str, workload_id: str) -> None:
        assert variant in {"baseline", "treatment"}
        self.variant = variant
        self.workload_id = workload_id

    # Parameters control behavior and are overridden in subclasses per workload
    base_engagement_prob: float = 0.6
    treatment_engagement_uplift: float = 0.1

    base_completion_prob: float = 0.55
    treatment_completion_uplift: float = 0.1

    base_learning_minutes_mean: float = 40.0
    treatment_learning_minutes_uplift: float = 10.0

    base_assessment_improvement_mean: float = 5.0
    treatment_assessment_improvement_uplift: float = 3.0

    def _rng(self) -> random.Random:
        # Derive a deterministic seed per workload+variant so runs are stable
        compounded_seed = hash((GLOBAL_SEED, self.workload_id, self.variant)) & 0xFFFFFFFF
        return random.Random(compounded_seed)

    def _engagement_prob(self) -> float:
        if self.variant == "baseline":
            return self.base_engagement_prob
        return min(1.0, self.base_engagement_prob + self.treatment_engagement_uplift)

    def _completion_prob(self) -> float:
        if self.variant == "baseline":
            return self.base_completion_prob
        return min(1.0, self.base_completion_prob + self.treatment_completion_uplift)

    def _learning_minutes_mean(self) -> float:
        if self.variant == "baseline":
            return self.base_learning_minutes_mean
        return self.base_learning_minutes_mean + self.treatment_learning_minutes_uplift

    def _assessment_improvement_mean(self) -> float:
        if self.variant == "baseline":
            return self.base_assessment_improvement_mean
        return self.base_assessment_improvement_mean + self.treatment_assessment_improvement_uplift

    def _simulate_user(self, rng: random.Random) -> Dict[str, float]:
        """Simulate a single user trajectory for this workload and variant.

        Returns a dict with numeric fields used for aggregation.
        """

        # Weekly engagement indicator for a short fixed window (e.g., 4 weeks)
        weeks = 4
        engaged_weeks = 0
        for _ in range(weeks):
            if rng.random() < self._engagement_prob():
                engaged_weeks += 1

        was_active = engaged_weeks > 0

        # Learning minutes for the whole pathway; simulate as log-normal-ish
        if was_active:
            mean_minutes = self._learning_minutes_mean()
            sigma = 0.4  # modest variability
            # Use log-normal via exp(mu + sigma * Z)
            mu = math.log(max(mean_minutes, 1.0)) - 0.5 * sigma**2
            minutes = math.exp(mu + sigma * rng.gauss(0.0, 1.0))
        else:
            minutes = 0.0

        # Completion probability only if engaged
        if was_active and rng.random() < self._completion_prob():
            completed = 1.0
        else:
            completed = 0.0

        # Assessment improvement: non-negative, scaled by minutes & variant mean
        base_improvement = max(0.0, rng.gauss(self._assessment_improvement_mean(), 2.0))
        # Simple cap and scaling
        improvement = min(base_improvement * (1.0 + 0.5 * (minutes / 60.0)), 30.0)

        return {
            "completed": float(completed),
            "minutes": float(minutes),
            "active": 1.0 if was_active else 0.0,
            "improvement": float(improvement),
        }

    def run_simulation(self, num_users: int) -> SimulationResult:
        rng = self._rng()
        outcomes: List[Dict[str, float]] = []
        for _ in range(num_users):
            outcomes.append(self._simulate_user(rng))

        if not outcomes:
            return SimulationResult(0.0, 0.0, 0.0, 0.0)

        n = float(len(outcomes))
        completion_rate = sum(o["completed"] for o in outcomes) / n
        avg_minutes = sum(o["minutes"] for o in outcomes) / n
        avg_improvement = sum(o["improvement"] for o in outcomes) / n
        weekly_active_rate = sum(o["active"] for o in outcomes) / n

        return SimulationResult(
            pathway_completion_rate=completion_rate,
            avg_learning_minutes=avg_minutes,
            avg_assessment_improvement=avg_improvement,
            weekly_active_learners_rate=weekly_active_rate,
        )


class GuidedLearningPathwayWorkload(BaseWorkload):
    """Simulated multi-week structured learning with assessments."""

    base_engagement_prob = 0.65
    treatment_engagement_uplift = 0.12

    base_completion_prob = 0.55
    treatment_completion_uplift = 0.12

    base_learning_minutes_mean = 45.0
    treatment_learning_minutes_uplift = 15.0

    base_assessment_improvement_mean = 6.0
    treatment_assessment_improvement_uplift = 4.0


class OnTheJobPerformanceSupportWorkload(BaseWorkload):
    """Simulated short performance-support interactions on the job."""

    base_engagement_prob = 0.5
    treatment_engagement_uplift = 0.15

    base_completion_prob = 0.4  # proxy for resolving enough tasks to count as completion
    treatment_completion_uplift = 0.1

    base_learning_minutes_mean = 20.0
    treatment_learning_minutes_uplift = 8.0

    base_assessment_improvement_mean = 3.0
    treatment_assessment_improvement_uplift = 2.5


class CareerAndSkillsCoachingWorkload(BaseWorkload):
    """Simulated career exploration and skills planning journeys."""

    base_engagement_prob = 0.55
    treatment_engagement_uplift = 0.1

    base_completion_prob = 0.45
    treatment_completion_uplift = 0.12

    base_learning_minutes_mean = 35.0
    treatment_learning_minutes_uplift = 10.0

    base_assessment_improvement_mean = 4.5
    treatment_assessment_improvement_uplift = 3.5


WORKLOAD_CLASS_MAP = {
    "Guided_learning_pathway_support": GuidedLearningPathwayWorkload,
    "On_the_job_performance_support": OnTheJobPerformanceSupportWorkload,
    "Career_and_skills_coaching": CareerAndSkillsCoachingWorkload,
}
