from __future__ import annotations

from difflib import unified_diff
from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: uv run python scripts/check_openapi.py <snapshot-path>")
    snapshot_path = Path(sys.argv[1]).resolve()
    expected = snapshot_path.read_text(encoding="utf-8") if snapshot_path.exists() else ""
    actual = render_openapi_json()
    if actual == expected:
        print(f"OpenAPI snapshot matches: {snapshot_path}")
        return 0
    print(f"OpenAPI contract drift detected: {snapshot_path}")
    print("Run `pnpm openapi:update` after reviewing the change.")
    diff = unified_diff(
        expected.splitlines(),
        actual.splitlines(),
        fromfile=f"{snapshot_path.name} (snapshot)",
        tofile=f"{snapshot_path.name} (generated)",
        lineterm="",
    )
    for line in diff:
        print(line)
    return 1


def render_openapi_json() -> str:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "apps" / "api" / "src"))
    from db_monitor_api.main import app
    import json

    return json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
