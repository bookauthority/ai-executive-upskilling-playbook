import json
import os
import platform
from pathlib import Path

from experiment.config import CHAPTER_NUMBER, EXPERIMENT_ID, WORKLOAD_IDS
from experiment.simulation import run_all_workloads
from experiment.evidence_writer import build_evidence_object, write_evidence


def main() -> None:
    """Run all simulated workloads and write standardized evidence.

    The function orchestrates the following steps:
    1. Run synthetic experiments for each workload, producing per-run metrics.
    2. Collect environment metadata.
    3. Build a JSON-serializable evidence object matching the required schema.
    4. Write the object to BOOKMAS_EVIDENCE_DIR/results.json (default /evidence).
    """\
    
    # 1. Run workloads (deterministic synthetic simulations)
    runs = run_all_workloads()

    # 2. Environment metadata
    env_info = {
        "os": os.name,
        "python": platform.python_version(),
    }

    # 3. Build evidence object
    evidence = build_evidence_object(
        chapter=CHAPTER_NUMBER,
        experiment_id=EXPERIMENT_ID,
        environment=env_info,
        runs=runs,
    )

    # 4. Determine evidence directory
    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    write_evidence(evidence, Path(evidence_dir))


if __name__ == "__main__":  # pragma: no cover - trivial dispatch
    main()
