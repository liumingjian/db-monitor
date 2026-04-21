from __future__ import annotations

import json
from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: uv run python scripts/export_openapi.py <output-path>")
    output_path = Path(sys.argv[1]).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_openapi_json(), encoding="utf-8")
    return 0


def render_openapi_json() -> str:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "apps" / "api" / "src"))
    from db_monitor_api.main import app

    return json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
