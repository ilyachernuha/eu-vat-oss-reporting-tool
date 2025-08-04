# Check if Python is available
try {
    $python = Get-Command python -ErrorAction Stop
} catch {
    Write-Error "Python is not available in PATH."
    exit 1
}

# Create virtual environment if it doesn't exist
if (-Not (Test-Path ".venv")) {
    Write-Output "Creating virtual environment..."
    python -m venv .venv
} else {
    Write-Output "Virtual environment already exists. Skipping creation."
}

# Activate virtual environment
$venvActivate = ".\.venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    Write-Output "Activating virtual environment..."
    & $venvActivate
} else {
    Write-Error "Could not find activation script at $venvActivate"
    exit 1
}

# Install dependencies
if (Test-Path "requirements.txt") {
    Write-Output "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
} else {
    Write-Warning "requirements.txt not found. Skipping package installation."
}

# Run main script
if (Test-Path "main.py") {
    Write-Output "Running main.py..."
    python .\main.py
} else {
    Write-Error "main.py not found. Exiting."
    exit 1
}
