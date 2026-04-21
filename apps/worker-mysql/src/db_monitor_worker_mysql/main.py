"""MySQL metrics worker operational entrypoint."""

import json

from db_monitor_pipeline.process_settings import ProcessMode, load_worker_process_settings
from db_monitor_pipeline.processes import build_worker_process
from . import get_app_name


def main() -> None:
    settings = load_worker_process_settings()
    process = build_worker_process(settings)
    result = (
        process.run_once()
        if settings.mode is ProcessMode.ONESHOT
        else process.run_loop(max_cycles=settings.max_cycles)
    )
    print(
        json.dumps(
            {
                "error": result.error,
                "mode": settings.mode.value,
                "next_retry_at": None
                if result.next_retry_at is None
                else result.next_retry_at.isoformat(),
                "process": get_app_name(),
                "processed_metrics": result.processed_metrics,
                "retry_attempt": result.retry_attempt,
                "status": result.status,
            }
        )
    )
    if result.status == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
