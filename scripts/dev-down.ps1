$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "docker is required on PATH to stop local foundation dependencies."
}

docker compose -f compose.yaml down
