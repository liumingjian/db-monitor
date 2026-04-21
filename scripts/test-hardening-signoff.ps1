$ErrorActionPreference = "Stop"

pnpm lint
pnpm typecheck
uv run ruff check .
uv run mypy apps tests gates
uv run pytest tests
powershell -ExecutionPolicy Bypass -File ./scripts/test-api-runtime-readiness.ps1
powershell -ExecutionPolicy Bypass -File ./scripts/test-background-processes.ps1
powershell -ExecutionPolicy Bypass -File ./scripts/test-schema-bootstrap.ps1
powershell -ExecutionPolicy Bypass -File ./scripts/test-recovery-paths.ps1
pnpm smoke
