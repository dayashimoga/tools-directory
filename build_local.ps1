$ErrorActionPreference = "Continue"

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🚀 Automated Venv Build & Test Sequence Started" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 1. Create Virtual Environment
Write-Host "`n[1/5] Creating temporary Python Virtual Environment (.venv_temp)..." -ForegroundColor Yellow
python -m venv .venv_temp

# 2. Activate Virtual Environment
Write-Host "[2/5] Activating Virtual Environment and installing dependencies..." -ForegroundColor Yellow
& .venv_temp\Scripts\python.exe -m pip install --upgrade pip | Out-Null
& .venv_temp\Scripts\python.exe -m pip install -r requirements.txt pytest pytest-cov responses | Out-Null

# 3. Run Pytest Suite
Write-Host "`n[3/5] Executing Pytest coverage suite natively..." -ForegroundColor Yellow
& .venv_temp\Scripts\python.exe -m pytest --cov=scripts
$TestExitCode = $LASTEXITCODE

# 4. Build Static HTML
Write-Host "`n[4/5] Compiling Jinja templates and building static directory..." -ForegroundColor Yellow
& .venv_temp\Scripts\python.exe -m scripts.build_directory
& .venv_temp\Scripts\python.exe -m scripts.generate_sitemap

# 5. Teardown
Write-Host "`n[5/5] Tearing down temporary Virtual Environment..." -ForegroundColor Yellow
Remove-Item -Recurse -Force .venv_temp

if ($TestExitCode -ne 0) {
    Write-Host "`n❌ Pipeline finished with test errors. Virtual Environment has been removed." -ForegroundColor Red
    exit 1
} else {
    Write-Host "`n✅ Pipeline completed successfully! HTML rebuilt and Tests passed." -ForegroundColor Green
    exit 0
}
