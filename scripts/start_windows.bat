@echo off
rem Double-click to start WikiAligner on Windows.
rem The first start installs Python and the dependencies (about 1 GB, needs internet);
rem later starts take a few seconds.
cd /d "%~dp0\.."
set "PATH=%USERPROFILE%\.local\bin;%PATH%"
where uv >nul 2>nul
if errorlevel 1 (
  echo Installing uv ^(Python package manager^)...
  powershell -NoProfile -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
)
uv run --no-dev --python 3.12 -m wikialigner %*
if errorlevel 1 (
  echo.
  echo WikiAligner stopped with an error.
  pause
)
