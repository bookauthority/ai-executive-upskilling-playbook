# GenAI Learning Copilot RCT Simulation (Chapter 8)

This project is a **self-contained, offline Python 3.11+ experiment** that simulates the randomized controlled trial (RCT) described in the chapter specification:

> **Experiment ID:** `exp-8-genai-learning-copilot-rct-v1`
>
> **Chapter 8:** Building GenAI Coaching and Copilot Experiences for Employees

It does **not** call external LLMs or services. Instead, it provides:

- A small, deterministic **baseline** experience (static guidance only).
- A small, deterministic **treatment** experience ("copilot" with rule-based conversational guidance, pseudo-RAG, and guardrails).
- A simple, reproducible **simulation of employee learning journeys** under each arm.
- An **evidence writer** that emits `/evidence/results.json` matching the required contract.
- **Unit tests** that validate the evidence structure and basic fairness/invariants.

The goal is to illustrate how to structure:

- Copilot vs. baseline behavior.
- Workloads and metrics instrumentation.
- RCT-style evidence collection.

All logic uses the Python standard library only; there are **no external dependencies**.

---

## Project Layout

- `run.py` – Entry point. Runs the simulation for all workloads and writes evidence.
- `experiment/__init__.py` – Package init (empty, for cleanliness).
- `experiment/config.py` – Constants and configuration values.
- `experiment/workloads.py` – Baseline and treatment implementations for each workload.
- `experiment/simulate.py` – RCT simulation engine that runs workloads and collects metrics.
- `experiment/evidence.py` – Evidence file schema helper and writer.
- `tests/test_experiment.py` – Unit tests for schema and basic behavior.
- `requirements.txt` – Empty runtime dependencies (only `unittest` from stdlib is used).

---

## Workloads Implemented

The code implements three workloads mirroring the specification:

1. `Guided_learning_pathway_support`
2. `On_the_job_performance_support`
3. `Career_and_skills_coaching`

Each workload is run with both **baseline** and **treatment** variants.

For each workload/variant pair, several **simulated employees** are run through a tiny deterministic model of behavior:

- Engagement probability and learning time.
- Pathway completion probability.
- Skills assessment improvement.

Treatment parameters are slightly more favorable (higher engagement and improvement) to reflect the hypothesis. The simulation is deterministic due to fixed random seeds.

---

## Metrics in This Offline Sandbox

Per the runtime contract, **every metric value is computed from actual code execution** in this sandbox. There are no wall-clock times, error rates, or external service metrics.

Each simulated run yields numeric metrics such as:

- `pathway_completion_rate` – Completion rate across the simulated cohort (0.0–1.0).
- `avg_learning_minutes` – Average learning minutes per simulated user.
- `avg_assessment_improvement` – Average improvement in normalized skills assessment scores.
- `weekly_active_learners_rate` – Share of simulated users with at least one learning interaction.

The exact metric set is defined in `experiment/simulate.py`. Metrics that require external systems or real users (e.g., NPS, true safety violations, ticket volume) are **not** reported here because they cannot be reliably measured in this offline environment.

---

## Evidence Output Schema

Running `python run.py` produces `/evidence/results.json` with the exact top-level structure:

```json
{
  "chapter": 8,
  "experiment_id": "exp-8-genai-learning-copilot-rct-v1",
  "environment": {
    "os": "...",
    "python": "..."
  },
  "runs": [
    {
      "variant": "baseline",
      "workload_id": "Guided_learning_pathway_support",
      "run_id": "...",
      "success": true,
      "metrics": {
        "pathway_completion_rate": 0.58,
        "avg_learning_minutes": 42.0,
        "avg_assessment_improvement": 7.5,
        "weekly_active_learners_rate": 0.75
      }
    },
    {
      "variant": "treatment",
      "workload_id": "Guided_learning_pathway_support",
      "run_id": "...",
      "success": true,
      "metrics": { ... }
    },
    ... more runs ...
  ],
  "notes": "..."
}
``

Constraints enforced by tests:

- `chapter` is integer `8`.
- `experiment_id` matches the provided spec exactly.
- `environment.os` and `environment.python` are non-empty strings.
- `runs` is a non-empty list.
- Every run has valid `variant`, `workload_id`, `run_id`, `success`, and `metrics` fields.
- Every metric value is a finite JSON number (no `null`, strings, lists, dicts, or booleans).
- At least one **baseline** and one **treatment** run exist for each workload.

Extra top-level fields beyond this schema are allowed but are treated as annotations, not measurements.

---

## Baseline vs. Treatment Implementations

Both baseline and treatment experiences are modeled as small Python classes implementing a shared interface:

- `run_simulation(num_users: int) -> dict`

Baseline characteristics (non-GenAI guidance):

- Static modules and guidance.
- Lower probabilities for high engagement and completion.
- Smaller average skills assessment improvements.

Treatment characteristics (GenAI copilot):

- Simulated conversational planning and micro-plans.
- Higher probabilities for engagement and completion.
- Larger expected assessment gains.
- Simple safety guardrails (e.g., rejecting disallowed topics and routing to human escalation in the stub).

The actual “copilot” logic uses rule-based text snippets to keep the project runnable without a live LLM, but the orchestration and measurement mirrors a realistic design.

---

## How to Run

From the project root:

1. **Run the experiment simulation**

```bash
python run.py
```

This will:

- Detect the environment (OS and Python version).
- Run all workloads for baseline and treatment.
- Write `/evidence/results.json` (using `BOOKMAS_EVIDENCE_DIR` if set, otherwise `/evidence`).

2. **Run tests**

```bash
python -m unittest discover -s tests -p "test_*.py"
```

The tests verify:

- Evidence file exists and is valid JSON.
- Schema rules described above.
- Presence of at least one baseline and one treatment run for each workload.
- Deterministic behavior given a fixed global random seed.

---

## Extending the Project

You can adapt this skeleton to:

- Plug in a real LLM backend and RAG pipeline where the rule-based copilot sits.
- Swap the simple synthetic user model for real event and assessment data.
- Add more realistic safety checks and escalation logging.
- Implement full metric coverage from the detailed experiment specification.

All core orchestration code is in `experiment/simulate.py` and `experiment/workloads.py`, making it easy to extend while reusing the evidence format and tests.
