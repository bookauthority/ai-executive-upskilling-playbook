# Chapter 7 Experiment: Implementing AI-Powered Skills Matching and Recommendations

This project is a **self-contained, offline Python 3.11+ experiment** for:

- **Chapter:** 7 – Implementing AI-Powered Skills Matching and Recommendations  
- **Experiment ID:** `exp-07-skills-rec-matching-v1`

It simulates a baseline **rule-based** skills recommender and a treatment **AI-style embedding** recommender on synthetic data, then writes results into an evidence file with a strict schema.

The goal is not to train a production model but to:

- Demonstrate **implementation-level patterns** for skills-based recommendation.  
- Provide a **reproducible experiment** that can be adapted to real data.  
- Show how to produce **measurable outcomes** and a structured evidence artifact.

All code uses only the Python **standard library** (no external dependencies).

---

## Project Structure

```text
.
├── README.md
├── requirements.txt
├── run.py
├── skills_rec
│   ├── __init__.py
│   ├── config.py
│   ├── data_generation.py
│   ├── models.py
│   ├── experiment.py
│   └── metrics.py
└── tests
    ├── __init__.py
    └── test_experiment.py
```

### Key Modules

- `skills_rec/config.py` – Static configuration including chapter number, experiment ID, workloads, and random seed.
- `skills_rec/data_generation.py` – Deterministic synthetic data generation for employees, catalog items, and interaction probabilities.
- `skills_rec/models.py` – Baseline and treatment recommendation logic:
  - Baseline: rule-based overlapping-skills scorer.
  - Treatment: simple embedding-based scorer approximating AI behavior.
- `skills_rec/metrics.py` – Simple metrics for simulated engagement (CTR-like, completion-like) using deterministic random draws.
- `skills_rec/experiment.py` – Orchestrates runs per workload and variant, collects metrics, and prepares evidence data.
- `run.py` – Entry point. Runs the synthetic experiment and writes `/evidence/results.json` (location overridable via `BOOKMAS_EVIDENCE_DIR`).
- `tests/test_experiment.py` – Validates the evidence schema and basic properties of the experiment.

---

## How the Prototype Works

### 1. Synthetic Skills Graph & Data

We simulate a minimal **skills graph-like structure**:

- Employees with skills and role families.
- Catalog items (learning/projects/roles) with `skills_required`, `role_family`, flags (`is_mandatory`, `is_strategic`).
- Segments (business unit, region, seniority) for potential fairness analysis.

Nodes and edges are implicit in Python data structures, but the schema aligns logically with the specification's `skills_graph` entity.

### 2. Baseline Recommender

Implements the rule-based logic from the specification:

- **Filter** catalog items by role family or overlapping skills.
- **Score** by overlapping skill count; boost mandatory and strategic items.
- **Rank** and take top-N recommendations.

This is implemented in `BaselineRecommender.recommend()`.

### 3. Treatment (AI-style) Recommender

Implements a lightweight, deterministic **embedding-style model** (no external libraries):

- Creates **skill vectors** on a 2D plane.
- Employee embedding = average of their skill vectors.
- Item embedding = average of its required skill vectors.
- Relevance score = cosine similarity + small mandatory/strategic adjustments − simple category frequency penalty.

This approximates the *pattern* of an AI skills graph recommender without heavy dependencies.

Implemented in `EmbeddingRecommender.recommend()` and helper functions in `skills_rec/models.py`.

### 4. Simulated Engagement & Metrics

For each workload (`learning_recommendations`, `project_matching`, `role_and_internal_mobility`):

- We compute a **quality score** for each (employee, top-N recommendations) pair.
- Convert that score into a **probability of engagement** using a logistic-like mapping.
- Sample **binary outcomes** (click/engage vs. not) with `random.Random` using a fixed seed.

Measured numerical metrics per run include:

- `engagement_rate` – Simulated CTR-like metric (0–1).  
- `avg_score` – Average recommendation quality score (0–1).  
- `n_employees` – Number of employees simulated (count).  
- `n_items` – Number of items in the catalog (count).

These are **actual, instrumented measurements** from the synthetic run, not fabricated constants.

### 5. Evidence File Schema

`run.py` writes JSON to `${BOOKMAS_EVIDENCE_DIR:-/evidence}/results.json`:

```json
{
  "chapter": 7,
  "experiment_id": "exp-07-skills-rec-matching-v1",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline",
      "workload_id": "learning_recommendations",
      "run_id": "...",
      "success": true,
      "metrics": {"engagement_rate": 0.23, "avg_score": 0.58, ...}
    },
    {
      "variant": "treatment",
      "workload_id": "learning_recommendations",
      "run_id": "...",
      "success": true,
      "metrics": {"engagement_rate": 0.29, "avg_score": 0.71, ...}
    }
  ],
  "notes": "... additional text ..."
}
```

- At least **one baseline and one treatment run per workload** are produced.  
- All **metric values** are **finite numbers** (no strings, `null`, dicts, etc.).
- Additional contextual fields (e.g., internal debug structures) go outside the `metrics` objects.

The included unit tests assert this exact contract.

---

## Running the Experiment

### Requirements

- Python **3.11+**
- No external dependencies (standard library only).

### 1. Install (optional virtual environment)

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the experiment

By default, evidence is written to `/evidence/results.json`. In the sandbox this directory is writable.

```bash
mkdir -p /evidence  # if needed
python run.py
```

To override the evidence directory:

```bash
export BOOKMAS_EVIDENCE_DIR=/tmp/evidence
mkdir -p "$BOOKMAS_EVIDENCE_DIR"
python run.py
cat "$BOOKMAS_EVIDENCE_DIR/results.json"
```

### 3. Run tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## Adapting to Real Data

To adapt this to a real organizational setting:

1. **Replace synthetic generation** (`skills_rec/data_generation.py`) with loaders from your HRIS/LMS/project systems, matched to the schemas described in the specification.
2. Replace the toy embedding logic in `skills_rec/models.py` with:
   - Graph embeddings (e.g., Node2Vec), or
   - Matrix factorization / neural recommenders.
3. Extend `skills_rec/metrics.py` to compute the KPIs from the spec (CTR, completion rate, fairness gaps, etc.) from real interaction logs.
4. Keep the **evidence schema** stable so that automated validators can consume experiment outputs consistently across chapters and experiments.

The current implementation is intentionally simple and deterministic to serve as a clear, reproducible reference for executives and engineering teams.
