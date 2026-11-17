# Experiment 9 – Experimentation and Evidence: Measuring What Works at Scale

This self-contained Python 3.11+ project simulates an experimentation and
measurement framework for autonomous AI upskilling initiatives, aligned with
chapter 9 of the AI Executive Upskilling playbook:

> **"Experimentation and Evidence: Measuring What Works at Scale"**

It includes:

- A simple synthetic data generator approximating:
  - A/B testing of learning experiences (Workload 1)
  - Multi‑arm recommendation algorithm experiments (Workload 2)
  - Cohort and longitudinal tracking (Workload 3)
- A small internal analytics layer that mimics the **evidence_schema** given in
  the specification (experiment, metric_result, effect_estimate, cohort_summary).
- A runtime that produces standardized evidence in `/evidence/results.json`
  following the required contract for this chapter.

The implementation is **offline, deterministic, and bounded**. It uses only the
Python standard library and writes no files outside the project tree and the
`/evidence` directory.

---

## Project Layout

```text
.
├── README.md
├── requirements.txt
├── run.py
├── experiment
│   ├── __init__.py
│   ├── config.py
│   ├── data_generation.py
│   ├── metrics.py
│   ├── simulation.py
│   └── evidence_writer.py
└── tests
    └── test_experiment.py
```

### Key Modules

- `experiment/config.py`
  - Contains static configuration reflecting the chapter specification:
    - Chapter number and experiment ID
    - Metric names used in the simulation
    - Workload identifiers for Workloads 1–3

- `experiment/data_generation.py`
  - Provides deterministic random number helpers and synthetic data generation
    utilities.
  - Simulates learners, skills, and performance-based outcomes for each
    workload.

- `experiment/metrics.py`
  - Defines simple metric computations from synthetic data, including:
    - `learning_pathway_completion_rate`
    - `skill_proficiency_gain`
    - `on_job_performance_index`
  - Designed to be consistent across baseline and treatment so comparisons are
    fair.

- `experiment/simulation.py`
  - Orchestrates synthetic experiments for:
    - **Workload 1**: A/B comparison of two AI learning experiences.
    - **Workload 2**: Multi‑arm recommendation comparison.
    - **Workload 3**: Cohort and longitudinal tracking.
  - Returns metrics suitable for the evidence writer.

- `experiment/evidence_writer.py`
  - Builds and writes the evidence JSON file to the directory pointed to by the
    `BOOKMAS_EVIDENCE_DIR` environment variable (default `/evidence`).
  - Ensures compliance with the exact schema required by the runtime contract.

- `run.py`
  - Entry point for running all three workloads.
  - Gathers per‑run metrics and writes `/evidence/results.json`.

- `tests/test_experiment.py`
  - Uses `unittest` from the standard library.
  - Verifies that `run.py` produces a JSON file matching the required schema
    and that key structural expectations hold (e.g., at least one baseline and
    one treatment run per workload).

---

## Evidence File Contract

Running `python run.py` will produce a file at
`$BOOKMAS_EVIDENCE_DIR/results.json` (default `/evidence/results.json`) with the
following structure:

```jsonc
{
  "chapter": 9,
  "experiment_id": "exp-09-exec-ai-upskilling-measurement-framework-v1",
  "environment": {
    "os": "...",          // e.g., "posix" or "nt"
    "python": "3.11.0"    // full version string
  },
  "runs": [
    {
      "variant": "baseline",     // or "treatment"
      "workload_id": "workload1_ab_experience", // stable ID
      "run_id": "...",          // unique within workload + variant
      "success": true,           // did the run complete without internal errors
      "metrics": {
        "learning_pathway_completion_rate": 0.63,
        "skill_proficiency_gain": 6.2,
        "on_job_performance_index": 0.51
      }
    },
    {
      "variant": "treatment",
      "workload_id": "workload1_ab_experience",
      "run_id": "...",
      "success": true,
      "metrics": {
        "learning_pathway_completion_rate": 0.69,
        "skill_proficiency_gain": 7.4,
        "on_job_performance_index": 0.54
      }
    },
    // ... similar objects for Workload 2 and 3
  ],
  "notes": "Textual description of how metrics were simulated and any limitations.",
  "simulation_details": { /* extra non-metric context */ }
}
```

**Important constraints satisfied by this project:**

- **At least one baseline and one treatment run for each workload.**
- **All metric values are numbers** (no strings, nulls, arrays, or objects).
- **Metrics come from actual computation** in this offline sandbox
  (synthetic but computed, never hard‑coded or fabricated after the fact).
- Additional non‑metric fields may appear at the top level (e.g.
  `simulation_details`) but **not** under `metrics`.

---

## Running the Experiment

### Prerequisites

- Python **3.11+**
- No external Python dependencies; the project uses only the standard library.

### Step 1 – Install (optional)

There are no third‑party requirements, but for completeness:

```bash
python -m pip install -r requirements.txt
```

This is effectively a no‑op since the requirements file is empty.

### Step 2 – Run the simulated experiments

From the project root (containing `run.py`):

```bash
# Optionally override the evidence directory; default is /evidence
export BOOKMAS_EVIDENCE_DIR=/evidence

python run.py
```

This will:

1. Simulate all three workloads (Workloads 1–3) with deterministic pseudo‑random
   data.
2. Compute the defined metrics for each variant.
3. Write `/evidence/results.json` with the required schema.

If `/evidence` does not exist, it will be created.

### Step 3 – Run tests

Run the unit tests to validate schema and basic behavior:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

The tests:

- Invoke `run.py` via `runpy.run_path` in‑process (no subprocess).
- Confirm that `results.json` exists and is valid JSON.
- Validate the root keys and data types.
- Assert that every `run` entry:
  - Has all required fields.
  - Contains a non‑empty numeric `metrics` mapping.
  - Uses only numeric values for metrics.
- Confirm that per‑workload there is at least one baseline and one treatment.

---

## How This Relates to Sections 9.1–9.8

- **9.1 – Why Pilots Don’t Prove Impact**
  - The code illustrates randomized A/B and multi‑arm designs, contrasting them
    with naive before/after comparisons (documented in comments and notes).

- **9.2 – Defining Success Metrics**
  - `experiment/metrics.py` encodes key metrics: completion, skill gain, and
    performance index.

- **9.3 – Designing A/B and Multivariate Tests**
  - `experiment/simulation.py` shows how individual‑level randomization can be
    implemented, including different effect sizes for treatment.

- **9.4 – Cohort & Longitudinal Tracking**
  - Workload 3 simulates two cohorts and tracks evolving skill profiles.

- **9.5 – Executive Dashboards**
  - `results.json` matches an evidence contract suitable as a back‑end for
    executive dashboards. A BI tool can ingest this file and render impact
    summaries, confidence intervals, and trends.

- **9.6 – Interpreting Results (Causality, Confounders)**
  - While this sandbox uses synthetic data without real confounders, the code
    structure and comments model where randomization checks and bias controls
    would live in a real system.

- **9.7 – Companion Repository**
  - This project plays the role of the `analytics` folder, providing templates
    for experiment simulation and evidence export.

- **9.8 – Case Study: Iterating via Experiments**
  - The deterministic synthetic differences between baseline and treatment
    variants illustrate how a program might iterate toward better skill and
    performance outcomes using experimentation evidence.

---

## Limitations

- All data are synthetic; no real HR, learning, or performance data are read.
- The simulation does **not** implement real statistical testing (p‑values,
  confidence intervals) to keep dependencies minimal and runtime small. Such
  quantities are not written in `metrics` and would require additional
  statistical libraries or implementations.
- Some metrics from the chapter specification (e.g., ROI, executive dashboard
  usage) cannot be meaningfully measured in this offline sandbox and are
  therefore omitted from the `metrics` objects.

These limitations are documented in the `notes` field of
`/evidence/results.json`.
