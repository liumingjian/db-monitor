$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$apiPort = 38100
$webPort = 38101
$apiUrl = "http://localhost:$apiPort"
$webUrl = "http://localhost:$webPort"
$apiOut = Join-Path $repoRoot ".tmp-smoke-api.out.log"
$apiErr = Join-Path $repoRoot ".tmp-smoke-api.err.log"
$webOut = Join-Path $repoRoot ".tmp-smoke-web.out.log"
$webErr = Join-Path $repoRoot ".tmp-smoke-web.err.log"

function Wait-Http200 {
    param(
        [string]$Url,
        [string]$Name
    )

    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        try {
            $response = Invoke-WebRequest $Url -UseBasicParsing -TimeoutSec 3
            if ($response.StatusCode -eq 200) {
                return
            }
        } catch {
        }
        Start-Sleep -Seconds 1
    }

    throw "$Name did not become healthy at $Url within 60 seconds."
}

function Show-LogIfPresent {
    param([string]$Path)

    if (Test-Path $Path) {
        Get-Content $Path
    }
}

$pnpm = Get-Command pnpm -ErrorAction Stop
$python = Join-Path $repoRoot ".venv\\Scripts\\python.exe"
if (-not (Test-Path $python)) {
    throw "Expected smoke Python runtime at $python"
}

Remove-Item $apiOut,$apiErr,$webOut,$webErr -ErrorAction SilentlyContinue

$apiProcess = $null
$webProcess = $null

try {
    & $pnpm.Source --filter web build

    $apiProcess = Start-Process `
        -FilePath $python `
        -ArgumentList "-m","uvicorn","db_monitor_api.smoke_main:app","--app-dir","apps/api/src","--host","127.0.0.1","--port",$apiPort `
        -WorkingDirectory $repoRoot `
        -RedirectStandardOutput $apiOut `
        -RedirectStandardError $apiErr `
        -PassThru

    Wait-Http200 -Url "$apiUrl/openapi.json" -Name "Smoke API"

    $webCommand = "& { `$env:DB_MONITOR_API_BASE_URL = '$apiUrl'; & '$($pnpm.Source)' --filter web exec next start --hostname 127.0.0.1 --port $webPort }"
    $webProcess = Start-Process `
        -FilePath "powershell" `
        -ArgumentList "-NoProfile","-Command",$webCommand `
        -WorkingDirectory $repoRoot `
        -RedirectStandardOutput $webOut `
        -RedirectStandardError $webErr `
        -PassThru

    Wait-Http200 -Url "$webUrl/login" -Name "Smoke Web"

    $env:PLAYWRIGHT_BASE_URL = $webUrl
    & $pnpm.Source exec playwright test -c playwright.smoke.config.ts
} catch {
    Write-Output "--- Smoke API stderr ---"
    Show-LogIfPresent -Path $apiErr
    Write-Output "--- Smoke API stdout ---"
    Show-LogIfPresent -Path $apiOut
    Write-Output "--- Smoke Web stderr ---"
    Show-LogIfPresent -Path $webErr
    Write-Output "--- Smoke Web stdout ---"
    Show-LogIfPresent -Path $webOut
    throw
} finally {
    Remove-Item Env:PLAYWRIGHT_BASE_URL -ErrorAction SilentlyContinue
    if ($webProcess -and -not $webProcess.HasExited) {
        Stop-Process -Id $webProcess.Id -Force
    }
    if ($apiProcess -and -not $apiProcess.HasExited) {
        Stop-Process -Id $apiProcess.Id -Force
    }
}
