#Requires -Version 5.1
# bedrock-code Windows installer
# Run with: powershell -ExecutionPolicy Bypass -File .\install.ps1

$ErrorActionPreference = 'Stop'

function Write-Step { param($n, $msg) Write-Host "" ; Write-Host "[$n] $msg" -ForegroundColor Cyan }
function Write-Ok   { param($msg) Write-Host "  OK  $msg" -ForegroundColor Green }
function Write-Info { param($msg) Write-Host "      $msg" -ForegroundColor DarkGray }
function Write-Err  { param($msg) Write-Host "  ERR $msg" -ForegroundColor Red ; Read-Host 'Press Enter to exit' ; exit 1 }

Write-Host ""
Write-Host "  bedrock-code installer" -ForegroundColor Cyan
Write-Host "  ----------------------" -ForegroundColor Cyan

# ── 1. Python 3.11+ ──────────────────────────────────────────────────────────
Write-Step '1/4' 'Checking Python'
try {
    $pyOut = & python --version 2>&1
    if ($pyOut -match 'Python (\d+)\.(\d+)') {
        $maj = [int]$Matches[1]
        $min = [int]$Matches[2]
        if ($maj -lt 3 -or ($maj -eq 3 -and $min -lt 11)) {
            Write-Err "Python 3.11+ required, found $pyOut. Get it from https://python.org"
        }
        Write-Ok $pyOut
    } else {
        Write-Err "Python not found. Download 3.11+ from https://python.org"
    }
} catch {
    Write-Err "Python not found. Download 3.11+ from https://python.org"
}

# ── 2. uv ─────────────────────────────────────────────────────────────────────
Write-Step '2/4' 'Checking uv'
$uvCmd = Get-Command uv -ErrorAction SilentlyContinue
if ($null -eq $uvCmd) {
    Write-Info 'uv not found -- installing via pip...'
    & python -m pip install uv --quiet
    if ($LASTEXITCODE -ne 0) { Write-Err 'pip install uv failed' }
    # Refresh PATH so uv is findable
    $env:PATH = [System.Environment]::GetEnvironmentVariable('PATH','Machine') + ';' +
                [System.Environment]::GetEnvironmentVariable('PATH','User')
    $uvCmd = Get-Command uv -ErrorAction SilentlyContinue
    if ($null -eq $uvCmd) { Write-Err 'uv installed but not found on PATH. Open a new terminal and re-run.' }
    Write-Ok 'uv installed'
} else {
    $uvVer = & uv --version 2>&1
    Write-Ok $uvVer
}

# ── 3. Install bedrock-code as a uv tool ─────────────────────────────────────
Write-Step '3/4' 'Installing bedrock-code'
$repoDir = $PSScriptRoot
if (-not $repoDir) { $repoDir = (Get-Location).Path }
Write-Info "Source: $repoDir"

Push-Location $repoDir
& uv tool install -e . --force
$exitCode = $LASTEXITCODE
Pop-Location

if ($exitCode -ne 0) { Write-Err 'uv tool install failed' }
Write-Ok 'bedrock-code installed'

# ── 4. Ensure ~/.local/bin is on PATH ────────────────────────────────────────
Write-Step '4/4' 'Checking PATH'
$uvBin = Join-Path $env:USERPROFILE '.local\bin'

$userPath = [System.Environment]::GetEnvironmentVariable('PATH', 'User')
if ($null -eq $userPath) { $userPath = '' }

if ($userPath -notlike "*$uvBin*") {
    $newPath = $uvBin + ';' + $userPath
    [System.Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')
    Write-Ok "Added $uvBin to user PATH (takes effect in new terminals)"
} else {
    Write-Ok 'PATH already includes uv bin directory'
}
$env:PATH = $uvBin + ';' + $env:PATH

$bcCmd = Get-Command bc -ErrorAction SilentlyContinue
if ($bcCmd) {
    Write-Ok "bc found at $($bcCmd.Source)"
} else {
    Write-Host ''
    Write-Host '  NOTE: Open a new terminal for PATH to take effect.' -ForegroundColor Yellow
}

# ── Done ──────────────────────────────────────────────────────────────────────
Write-Host ''
Write-Host '  Installation complete!' -ForegroundColor Green
Write-Host ''
Write-Host '  Next steps:' -ForegroundColor White
Write-Host '    1.  aws login    (SSO login if not already authenticated)' -ForegroundColor DarkGray
Write-Host '    2.  bc           (setup wizard launches on first run)' -ForegroundColor DarkGray
Write-Host '    3.  bc setup     (re-run wizard anytime)' -ForegroundColor DarkGray
Write-Host ''
