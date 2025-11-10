# This script assumes you are running it from the root of your project

# Step 1: Run ruff format
Write-Host "Running ruff format..."
ruff format .
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ruff format failed. Exiting." -ForegroundColor Red
    exit $LASTEXITCODE
}

# Step 2: Run ruff check with --fix
Write-Host "Running ruff check with --fix..."
ruff check . --fix
if ($LASTEXITCODE -ne 0) {
    Write-Host "Ruff check failed. Exiting." -ForegroundColor Red
    exit $LASTEXITCODE
}

# Step 3: Run pytest if the above steps are successful
Write-Host "Running pytest..."
pytest tests/
if ($LASTEXITCODE -ne 0) {
    Write-Host "Tests failed. Exiting." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "All checks and tests passed successfully!" -ForegroundColor Green