@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
  echo Install Python 3.11 or 3.12 from python.org, then try again.
  pause
  exit /b 1
)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
if not exist .venv\Scripts\python.exe (
  echo Could not create the virtual environment.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m pip install -r requirements-tested.txt
if errorlevel 1 (
  echo Installation failed. Check your internet connection and Python version.
  pause
  exit /b 1
)
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
pause
