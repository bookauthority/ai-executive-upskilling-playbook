import json
import os
import platform
from pathlib import Path

from experiment.simulate import run_full_experiment
from experiment.config import CHAPTER_NUMBER, EXPERIMENT_ID


def main() -> None:
    # Determine evidence directory (default /evidence)
    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    results_file = evidence_path / "results.json"

    environment = {
        "os": platform.platform(),
        "python": platform.python_version(),
    }

    results = run_full_experiment(environment=environment)

    with results_file.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, sort_keys=False)


if __name__ == "__main__":
    main()
