import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app.engine import DraftEngine


REQUEST_PATH = PROJECT_ROOT / "example_request_v7.json"
OUTPUT_PATH = PROJECT_ROOT / "regression_user_draft_v7.json"


def main():
    request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    results = DraftEngine().rank_candidates(**request)
    OUTPUT_PATH.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(results)} candidates to {OUTPUT_PATH.name}")


if __name__ == "__main__":
    main()
