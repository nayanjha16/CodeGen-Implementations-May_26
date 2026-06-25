# Windows PowerShell: create and activate virtual environment
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$VenvPath = Join-Path $ProjectRoot ".venv"

if (-not (Test-Path (Join-Path $VenvPath "Scripts\Activate.ps1"))) {
    Write-Host "Creating virtual environment at .venv ..."
    py -3.11 -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        python -m venv .venv
    }
}

Write-Host "Activating .venv ..."
& (Join-Path $VenvPath "Scripts\Activate.ps1")

Write-Host "Installing dependencies ..."
pip install -r requirements.txt

Write-Host ""
Write-Host "Done. Virtual environment is active."
Write-Host "Project root: $ProjectRoot"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  `$env:PYTHONPATH = (Get-Location).Path"
Write-Host "  python scripts/test_tend_loader.py"
Write-Host "  python scripts/run_baseline_eval.py --tend-config spider --max-samples 5"
