@echo off
setlocal EnableDelayedExpansion

echo.
echo   bedrock-code installer
echo   ----------------------
echo.

:: ── Step 1: Python 3.11+ ───────────────────────────────────────────────────
echo [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ERR  Python not found.
    echo        Download from https://python.org  (3.11 or newer)
    pause & exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
for /f "delims=. tokens=1,2" %%a in ("%PYVER%") do (
    set MAJOR=%%a & set MINOR=%%b
)
if %MAJOR% LSS 3 goto :badpython
if %MAJOR% EQU 3 if %MINOR% LSS 11 goto :badpython
echo    OK   Python %PYVER%
goto :checkuv

:badpython
echo   ERR  Python 3.11+ required (found %PYVER%).
echo        Download from https://python.org
pause & exit /b 1

:: ── Step 2: uv ─────────────────────────────────────────────────────────────
:checkuv
echo [2/4] Checking uv...
uv --version >nul 2>&1
if errorlevel 1 (
    echo        uv not found -- installing via pip...
    python -m pip install uv --quiet
    if errorlevel 1 (
        echo   ERR  Failed to install uv.
        pause & exit /b 1
    )
    echo    OK   uv installed
) else (
    for /f "tokens=*" %%v in ('uv --version') do echo    OK   %%v
)

:: ── Step 3: Install bedrock-code ───────────────────────────────────────────
echo [3/4] Installing bedrock-code...
uv tool install -e "%~dp0." --force
if errorlevel 1 (
    echo   ERR  Installation failed.
    pause & exit /b 1
)
echo    OK   bedrock-code installed

:: ── Step 4: PATH ───────────────────────────────────────────────────────────
echo [4/4] Adding to PATH...
set "UV_BIN=%USERPROFILE%\.local\bin"
:: Add to user PATH permanently via registry
for /f "tokens=2*" %%a in (
    'reg query "HKCU\Environment" /v PATH 2^>nul'
) do set "CURRENT_PATH=%%b"

echo !CURRENT_PATH! | findstr /i "%UV_BIN%" >nul
if errorlevel 1 (
    setx PATH "%UV_BIN%;!CURRENT_PATH!" >nul
    echo    OK   Added %UV_BIN% to PATH
) else (
    echo    OK   PATH already contains uv bin
)
set "PATH=%UV_BIN%;%PATH%"

bc --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo   NOTE: Open a new terminal for PATH changes to take effect.
) else (
    echo    OK   bc is ready
)

:: ── Done ───────────────────────────────────────────────────────────────────
echo.
echo   Installation complete!
echo.
echo   Next steps:
echo     1.  aws login          (if not already logged in)
echo     2.  bc                 (setup wizard on first run)
echo     3.  bc setup           (re-run wizard anytime)
echo.
pause
