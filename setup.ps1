$ErrorActionPreference = "Stop"

function Get-PythonCommand {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return "py"
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        return "python"
    }

    throw "Python is not installed or not available in PATH."
}

function Test-OllamaModel {
    param(
        [string]$ModelName
    )

    if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
        throw "Ollama is not installed or not available in PATH."
    }

    $models = ollama list
    if ($models -notmatch [regex]::Escape($ModelName)) {
        throw "Required Ollama model '$ModelName' was not found. Run: ollama pull $ModelName"
    }
}

$pythonCommand = Get-PythonCommand
$venvPath = ".venv"
$modelName = "gpt-oss-safeguard:20b"

Write-Host "Creating virtual environment..."
if (-not (Test-Path $venvPath)) {
    if ($pythonCommand -eq "py") {
        py -3 -m venv $venvPath
    } else {
        python -m venv $venvPath
    }
}

$venvPython = Join-Path $venvPath "Scripts\python.exe"

Write-Host "Installing Python dependencies..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "Checking Ollama model..."
Test-OllamaModel -ModelName $modelName

Write-Host "Setup completed successfully."
Write-Host "Run the app with: .venv\Scripts\python.exe -m streamlit run streamlit_app.py"