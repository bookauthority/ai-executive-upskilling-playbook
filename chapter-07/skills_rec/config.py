from __future__ import annotations

CHAPTER_NUMBER: int = 7
EXPERIMENT_ID: str = "exp-07-skills-rec-matching-v1"

# Deterministic random seed so that runs are reproducible
GLOBAL_RANDOM_SEED: int = 12345

# Workloads aligned with specification
WORKLOADS = [
    {
        "workload_id": "learning_recommendations",
        "description": "Synthetic learning recommendation interactions",
        "n_employees": 300,  # scaled-down but stable for tests
        "n_items": 400,
        "item_type": "learning",
    },
    {
        "workload_id": "project_matching",
        "description": "Synthetic project matching interactions",
        "n_employees": 200,
        "n_items": 120,
        "item_type": "project",
    },
    {
        "workload_id": "role_and_internal_mobility",
        "description": "Synthetic internal role recommendation interactions",
        "n_employees": 250,
        "n_items": 150,
        "item_type": "role",
    },
]

# Top-N recommendations per employee in each run
TOP_N: int = 10

# Single run per (workload, variant) keeps execution bounded and fast
RUNS_PER_VARIANT_PER_WORKLOAD: int = 1
