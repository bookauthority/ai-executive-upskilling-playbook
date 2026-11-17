from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from .config import GLOBAL_RANDOM_SEED, TOP_N
from .data_generation import CatalogItem, Employee


@dataclass
class ScoredItem:
    item_id: str
    score: float


class BaselineRecommender:
    """Rule-based recommender using overlapping skills and simple boosts.

    This follows the baseline logic described in the specifications.
    """

    def __init__(self, items: Sequence[CatalogItem]):
        self.items = list(items)

    @staticmethod
    def _score(emp: Employee, item: CatalogItem) -> float:
        overlap = len(set(emp.skills) & set(item.skills_required))
        base_score = float(overlap)
        if item.is_mandatory:
            base_score += 5.0
        if item.is_strategic:
            base_score += 2.0
        return base_score

    def recommend(self, emp: Employee, top_n: int = TOP_N) -> List[ScoredItem]:
        candidates: List[ScoredItem] = []
        for item in self.items:
            if item.role_family != emp.job_family and not (set(emp.skills) & set(item.skills_required)):
                continue
            score = self._score(emp, item)
            if score <= 0.0:
                continue
            candidates.append(ScoredItem(item_id=item.item_id, score=score))
        candidates.sort(key=lambda s: s.score, reverse=True)
        return candidates[:top_n]


class EmbeddingRecommender:
    """Simple embedding-style recommender.

    - Each skill is mapped to a deterministic 2D vector.
    - Employee embedding is the average of owned skill vectors.
    - Item embedding is the average of required skill vectors.
    - Score is cosine similarity plus small rule-based modifiers and a
      light category diversity penalty.
    """

    def __init__(self, items: Sequence[CatalogItem], skills: Sequence[str]):
        self.items = list(items)
        self.skills = list(skills)
        self.skill_vecs: Dict[str, Tuple[float, float]] = self._init_skill_vectors(self.skills)
        self.category_counts: Dict[str, int] = {}

    @staticmethod
    def _init_skill_vectors(skills: Sequence[str]) -> Dict[str, Tuple[float, float]]:
        # Deterministic pseudo-random 2D vectors on the unit circle.
        vecs: Dict[str, Tuple[float, float]] = {}
        for idx, sid in enumerate(skills):
            angle = (idx * 137.508) % 360  # an irrational step for pseudo-uniformity
            rad = math.radians(angle)
            vecs[sid] = (math.cos(rad), math.sin(rad))
        return vecs

    @staticmethod
    def _avg_vectors(vecs: Iterable[Tuple[float, float]]) -> Tuple[float, float]:
        xs, ys, n = 0.0, 0.0, 0
        for x, y in vecs:
            xs += x
            ys += y
            n += 1
        if n == 0:
            return 0.0, 0.0
        return xs / n, ys / n

    @staticmethod
    def _cosine(u: Tuple[float, float], v: Tuple[float, float]) -> float:
        ux, uy = u
        vx, vy = v
        num = ux * vx + uy * vy
        du = math.hypot(ux, uy)
        dv = math.hypot(vx, vy)
        if du == 0 or dv == 0:
            return 0.0
        return num / (du * dv)

    def _employee_vec(self, emp: Employee) -> Tuple[float, float]:
        return self._avg_vectors(self.skill_vecs.get(sid, (0.0, 0.0)) for sid in emp.skills)

    def _item_vec(self, item: CatalogItem) -> Tuple[float, float]:
        return self._avg_vectors(self.skill_vecs.get(sid, (0.0, 0.0)) for sid in item.skills_required)

    def _category_penalty(self, category: str) -> float:
        # Simple diversity pressure: categories that appear frequently
        # in previous rankings get a slightly higher penalty.
        freq = self.category_counts.get(category, 0)
        return min(0.05 * freq, 0.3)

    def recommend(self, emp: Employee, top_n: int = TOP_N) -> List[ScoredItem]:
        emp_vec = self._employee_vec(emp)
        scored: List[ScoredItem] = []

        # reset category counts per call to avoid cross-employee coupling
        self.category_counts = {}

        temp: List[Tuple[CatalogItem, float]] = []
        for item in self.items:
            # Loose eligibility filter based on any overlapping skill
            if not (set(emp.skills) & set(item.skills_required)):
                continue
            sim = self._cosine(emp_vec, self._item_vec(item))
            score = sim
            if item.is_mandatory:
                score += 0.3
            if item.is_strategic:
                score += 0.1
            temp.append((item, score))

        # Now apply category-based diversity penalty in sorted order
        temp.sort(key=lambda t: t[1], reverse=True)
        for item, base_score in temp:
            penalty = self._category_penalty(item.category)
            final_score = base_score - penalty
            self.category_counts[item.category] = self.category_counts.get(item.category, 0) + 1
            scored.append(ScoredItem(item_id=item.item_id, score=final_score))

        scored.sort(key=lambda s: s.score, reverse=True)
        return scored[:top_n]


def simulate_engagement(
    rng: random.Random,
    emp: Employee,
    ranked_items: Sequence[ScoredItem],
    catalog_index: Mapping[str, CatalogItem],
) -> Tuple[float, float]:
    """Simulate engagement for a list of ranked items.

    Returns (engagement_rate, avg_score) where:
      - engagement_rate is the fraction of items that generated a positive
        simulated engagement signal (0–1).
      - avg_score is the mean of max(0, score) normalized into [0,1] via a
        simple logistic-like mapping.
    """

    if not ranked_items:
        return 0.0, 0.0

    engagements = 0
    score_sum = 0.0

    # Heuristic: map algorithm score to probability via logistic on z-score.
    scores = [ri.score for ri in ranked_items]
    mean_s = sum(scores) / len(scores)
    var_s = sum((s - mean_s) ** 2 for s in scores) / max(len(scores) - 1, 1)
    std_s = math.sqrt(var_s) if var_s > 0 else 1.0

    def prob_from_score(s: float) -> float:
        z = (s - mean_s) / (std_s + 1e-6)
        # logistic squashing into [0,1]
        return 1.0 / (1.0 + math.exp(-z))

    for ri in ranked_items:
        item = catalog_index[ri.item_id]
        base_p = prob_from_score(ri.score)
        # clamp probabilities for safety
        p = max(0.01, min(0.99, base_p))
        if rng.random() < p:
            engagements += 1
        # Normalize score into [0,1] by sigmoid on z-score
        score_sum += p

    engagement_rate = engagements / len(ranked_items)
    avg_score = score_sum / len(ranked_items)
    return engagement_rate, avg_score
