$ErrorActionPreference = "Stop"

python3 -c "import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)" uv run pytest tests/ops/test_oracle_runtime_baseline.py tests/ops/test_macos_environment_entrypoints.py tests/api/control_plane/test_oracle_validation.py -q
pnpm test:oracle-runtime:doctor
pnpm test:control-plane:postgres
pnpm test:control-plane:oracle
