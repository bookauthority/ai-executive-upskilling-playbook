from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Tuple

from .config import GLOBAL_RANDOM_SEED
from .data_generation import CatalogItem, Employee, SyntheticWorld, build_item_index
from .models import BaselineRecommender, EmbeddingRecommender, simulate_engagement


@dataclass
class RunMetrics:
    engagement_rate: float
    avg_score: float
    n_employees: int
    n_items: int


@dataclass
class VariantResult:
    variant: str
    workload_id: str
    run_id: str
    metrics: RunMetrics


def run_single_variant(
    workload_id: str,
    item_type: str,
    n_employees: int,
    n_items: int,
    variant: str,
) -> VariantResult:
    # Derive a deterministic seed per (workload, variant)
    seed = GLOBAL_RANDOM_SEED + hash((workload_id, item_type, variant)) % 100_000
    rng = random.Random(seed)

    world = SyntheticWorld()
    from .data_generation import create_synthetic_world

    world = create_synthetic_world(n_employees=n_employees, n_items=n_items, item_type=item_type)

    if variant == "baseline":
        model = BaselineRecommender(world.items)
    elif variant == "treatment":
        model = EmbeddingRecommender(world.items, world.skills)
    else:
        raise ValueError(f"Unknown variant: {variant}")

    catalog_index: Mapping[str, CatalogItem] = build_item_index(world.items)

    total_engagement = 0.0
    total_score = 0.0
    count = 0

    for emp in world.employees:
        ranked = model.recommend(emp)
        engagement_rate, avg_score = simulate_engagement(rng, emp, ranked, catalog_index)
        total_engagement += engagement_rate
        total_score += avg_score
        count += 1

    if count == 0:
        engagement_rate = 0.0
        avg_score = 0.0
    else:
        engagement_rate = total_engagement / count
        avg_score = total_score / count

    run_id = f"{workload_id}_{variant}_run_0"
    metrics = RunMetrics(
        engagement_rate=engagement_rate,
        avg_score=avg_score,
        n_employees=len(world.employees),
        n_items=len(world.items),
    )
    return VariantResult(variant=variant, workload_id=workload_id, run_id=run_id, metrics=metrics)
