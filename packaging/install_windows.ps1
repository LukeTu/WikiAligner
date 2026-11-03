# One-step install for 64-bit Windows 10/11, in PowerShell:
#   irm https://github.com/LukeTu/WikiAligner/releases/latest/download/install_windows.ps1 | iex
# Installs for the current user, so no administrator rights are needed.
$ErrorActionPreference = "Stop"
$url = "https://github.com/LukeTu/WikiAligner/releases/latest/download/WikiAligner-Windows-x64-Setup.exe"
$setup = Join-Path $env:TEMP "WikiAligner-Setup.exe"

Write-Host "Downloading WikiAligner (under 1 GB)..."
& curl.exe -fL --retry 3 --progress-bar -o $setup $url
if ($LASTEXITCODE -ne 0) { throw "Download failed. Check the network connection, or download the installer from the Releases page." }

Write-Host "Installing..."
$p = Start-Process -FilePath $setup -ArgumentList "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART" -Wait -PassThru
if ($p.ExitCode -ne 0) { throw "The installer stopped with code $($p.ExitCode)." }
Remove-Item $setup -ErrorAction SilentlyContinue

$exe = Join-Path $env:LOCALAPPDATA "Programs\WikiAligner\WikiAligner.exe"
Write-Host "Installed $exe"
Start-Process $exe
