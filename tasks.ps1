param(
    [Parameter(Position = 0)]
    [ValidateSet("install", "build", "clean", "run", "help")]
    [string]$Task = "help",

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RemainingArgs
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Invoke-Install {
    python -m pip install -U pip
    python -m pip install -e .
}

function Invoke-Build {
    python -m pip install .[build]
    python -m PyInstaller --onefile --name animeflv init.py
    Write-Host "Built: dist\animeflv.exe"
}

function Invoke-Clean {
    if (Test-Path dist) { Remove-Item -Recurse -Force dist }
    if (Test-Path build) { Remove-Item -Recurse -Force build }
    if (Test-Path "*.spec") { Remove-Item -Force *.spec }
    if (Test-Path "__pycache__") { Remove-Item -Recurse -Force __pycache__ }
}

function Invoke-Run {
    if (-not $RemainingArgs -or $RemainingArgs.Count -eq 0) {
        Write-Host "Usage: .\tasks.ps1 run -- <anime> [-b chrome|safari] [-o 0] [-l -1]"
        return
    }
    python -m init @RemainingArgs
}

function Show-Help {
    Write-Host "Usage: .\tasks.ps1 <task> [args]"
    Write-Host ""
    Write-Host "Tasks:"
    Write-Host "  install   Upgrade pip and install editable deps"
    Write-Host "  build     Build single-file exe via PyInstaller"
    Write-Host "  clean     Remove build artifacts"
    Write-Host "  run       Run the CLI via python -m init"
}

switch ($Task) {
    "install" { Invoke-Install }
    "build" { Invoke-Build }
    "clean" { Invoke-Clean }
    "run" { Invoke-Run }
    default { Show-Help }
}
