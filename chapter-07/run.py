import json
import os
import platform
from datetime import datetime

from skills_rec.config import CHAPTER_NUMBER, EXPERIMENT_ID
from skills_rec.experiment import run_full_experiment


def main() -> None:
    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    results_path = os.path.join(evidence_dir, "results.json")

    runs, extra_notes = run_full_experiment()

    evidence = {
        "chapter": CHAPTER_NUMBER,
        "experiment_id": EXPERIMENT_ID,
        "environment": {
            "os": platform.platform(),
            "python": platform.python_version(),
        },
        "runs": runs,
        "notes": extra_notes,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
