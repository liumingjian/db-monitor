$ErrorActionPreference = "Stop"

python3 -c "import subprocess,sys; sys.exit(subprocess.run(sys.argv[1:], timeout=60).returncode)" uv run pytest tests/ops/test_prelaunch_rehearsal_packet.py tests/ops/test_launch_readiness_baseline.py tests/ops/test_release_baseline.py tests/ops/test_macos_environment_entrypoints.py -q
pnpm test:hardening:signoff
pnpm test:oracle-runtime:signoff
git diff --check
