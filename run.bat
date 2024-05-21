@echo off
setlocal

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Python 3 could not be found, please install Python 3 from https://www.python.org
    goto end
) else (
    echo Python 3 is already installed.
)

:: Variables
set "DEFAULT_VENV_PATH=.venv"
set "SCRIPT_DIR=%~dp0"
set "PYTHON_SCRIPT_PATH=%SCRIPT_DIR%start.py"
set "REQUIREMENTS_PATH=%SCRIPT_DIR%requirements.txt"
set "VENV_PATH=%1"
if "%VENV_PATH%"=="" set "VENV_PATH=%DEFAULT_VENV_PATH%"

:: Check if the virtual environment directory exists
if not exist "%VENV_PATH%" (
    echo Setting up Python virtual environment at %VENV_PATH%...
    python -m venv "%VENV_PATH%"
    call "%VENV_PATH%\Scripts\activate"
    pip install -r "%REQUIREMENTS_PATH%"
    where flask
    where gunicorn
    call "%VENV_PATH%\Scripts\deactivate"
    echo Virtual environment and dependencies are set up. Flask and Gunicorn paths verified.
) else (
    echo Virtual environment already exists at %VENV_PATH%.
)

:: Add virtual environment bin to PATH temporarily and activate the virtual environment
set "PATH=%VENV_PATH%\Scripts;%PATH%"
call "%VENV_PATH%\Scripts\activate"

:: Verifying the path for executables again to confirm
where flask
where gunicorn

:: Run the Python script
python "%PYTHON_SCRIPT_PATH%"

:: Deactivate the virtual environment
call "%VENV_PATH%\Scripts\deactivate"

:end
endlocal
echo Finished.
