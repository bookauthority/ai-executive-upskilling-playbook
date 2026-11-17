CHAPTER_NUMBER: int = 8
EXPERIMENT_ID: str = "exp-8-genai-learning-copilot-rct-v1"

# Workload identifiers are stable and must match spec naming where possible
WORKLOAD_IDS = [
    "Guided_learning_pathway_support",
    "On_the_job_performance_support",
    "Career_and_skills_coaching",
]

# Number of synthetic users simulated per workload/variant.
# Kept small for fast, bounded execution.
USERS_PER_RUN = 50

# Global random seed for deterministic simulations
GLOBAL_SEED = 42
