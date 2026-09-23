$ErrorActionPreference = "Stop"

Set-Location "D:\python_basic_project"

Write-Host "=================================================="
Write-Host "STEP 1: Git status and remote"
Write-Host "=================================================="
git status --short --branch
git remote -v

Write-Host ""
Write-Host "=================================================="
Write-Host "STEP 2: Create venv if needed"
Write-Host "=================================================="
if (-not (Test-Path ".venv")) {
    py -m venv .venv
}

. .\.venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "=================================================="
Write-Host "STEP 3: Install dependencies"
Write-Host "=================================================="
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host ""
Write-Host "=================================================="
Write-Host "STEP 4: Run unit tests"
Write-Host "=================================================="
python -m pytest tests/ -q

Write-Host ""
Write-Host "=================================================="
Write-Host "STEP 5: Syntax check"
Write-Host "=================================================="
python -m py_compile `
    main.py `
    desktop_widget.py `
    app/integrations.py `
    app/project_tracker.py `
    weekly_report.py

Write-Host ""
Write-Host "=================================================="
Write-Host "STEP 6: Import smoke test"
Write-Host "=================================================="
python -c "import main, desktop_widget, app.integrations, app.project_tracker, weekly_report; print('IMPORT_OK')"

Write-Host ""
Write-Host "=================================================="
Write-Host "STEP 7: Critical dependency check"
Write-Host "=================================================="
python -c "import aiogram, dotenv, requests, sqlite3; print('DEPENDENCIES_OK')"

Write-Host ""
Write-Host "=================================================="
Write-Host "STEP 8: Compile all Python files"
Write-Host "=================================================="
python -m compileall . -q

Write-Host ""
Write-Host "=================================================="
Write-Host "FINAL RESULT: CHECK PASSED"
Write-Host "=================================================="