CHAPTER_NUMBER: int = 9

# Experiment identifier from the provided specification
EXP_ERIMENT_ID_SPEC = "exp-09-exec-ai-upskilling-measurement-framework-v1"
# Preserve spelling above but export canonical constant below
EXPERIMENT_ID: str = EXP_ERIMENT_ID_SPEC

# Stable workload identifiers shared by baseline and treatment variants
WORKLOAD_IDS = {
    "workload1": "workload1_ab_experience",
    "workload2": "workload2_multiarm_recommendation",
    "workload3": "workload3_cohort_longitudinal",
}

# Metric names we will actually simulate and compute. These are a
# subset of the full metric catalog from the chapter specification,
# chosen such that they can be meaningfully produced in a small,
# offline sandbox.
METRIC_NAMES = [
    "learning_pathway_completion_rate",
    "skill_proficiency_gain",
    "on_job_performance_index",
]
