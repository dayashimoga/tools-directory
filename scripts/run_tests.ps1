# ============================================================
# QuickUtils API Directory — Local Test Runner (PowerShell)
# Runs the full test suite inside Docker. No local installs needed.
# ============================================================

param(
    [switch]$Build,
    [switch]$Serve,
    [switch]$Coverage,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

# Colors for output
function Write-Header($msg) { Write-Host "`n=== $msg ===" -ForegroundColor Cyan }
function Write-Success($msg) { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Fail($msg) { Write-Host "  ✗ $msg" -ForegroundColor Red }

if ($Help) {
    Write-Host @"
QuickUtils API Directory — Local Development Scripts

Usage:
    .\scripts\run_tests.ps1           Run full test suite with coverage
    .\scripts\run_tests.ps1 -Build    Build the static site
    .\scripts\run_tests.ps1 -Serve    Build and serve on http://localhost:8000
    .\scripts\run_tests.ps1 -Coverage Run tests with HTML coverage report
    .\scripts\run_tests.ps1 -Help     Show this help message

Prerequisites: Docker Desktop must be running.
"@
    exit 0
}

# Check Docker is available
try {
    docker version | Out-Null
    Write-Success "Docker is available"
} catch {
    Write-Fail "Docker is not running. Please start Docker Desktop."
    exit 1
}

if ($Serve) {
    Write-Header "Building and Serving Site"
    Write-Host "  Site will be available at http://localhost:8000" -ForegroundColor Yellow
    Write-Host "  Press Ctrl+C to stop." -ForegroundColor Yellow
    docker compose up --build serve
    exit $LASTEXITCODE
}

if ($Build) {
    Write-Header "Building Static Site"
    docker compose run --rm build
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Build completed. Output in dist/"
        $pageCount = (Get-ChildItem -Path "dist" -Recurse -Filter "*.html" -ErrorAction SilentlyContinue | Measure-Object).Count
        Write-Host "  Total HTML pages: $pageCount" -ForegroundColor Yellow
    } else {
        Write-Fail "Build failed."
    }
    exit $LASTEXITCODE
}

if ($Coverage) {
    Write-Header "Running Tests with HTML Coverage Report"
    docker compose run --rm test python -m pytest tests/ -v --cov=scripts --cov-report=html --cov-report=term-missing --cov-fail-under=90
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Tests passed! Open htmlcov/index.html for the report."
    } else {
        Write-Fail "Tests failed or coverage below 90%."
    }
    exit $LASTEXITCODE
}

# Default: Run tests with terminal coverage report
Write-Header "Running Full Test Suite"
docker compose run --rm test

if ($LASTEXITCODE -eq 0) {
    Write-Success "All tests passed with ≥90% coverage!"
} else {
    Write-Fail "Tests failed or coverage below 90%."
}

exit $LASTEXITCODE
