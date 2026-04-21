"""Metrics scheduler operational entrypoint."""

import json

from db_monitor_pipeline.process_settings import ProcessMode, load_scheduler_process_settings
from db_monitor_pipeline.processes import build_scheduler_process
from . import get_app_name


def main() -> None:
    settings = load_scheduler_process_settings()
    process = build_scheduler_process(settings)
    result = (
        process.run_once()
        if settings.mode is ProcessMode.ONESHOT
        else process.run_loop(max_cycles=settings.max_cycles)
    )
    print(
        json.dumps(
            {
                "dispatched_jobs": result.dispatched_jobs,
                "mode": settings.mode.value,
                "process": get_app_name(),
                "status": result.status,
            }
        )
    )


if __name__ == "__main__":
    main()
