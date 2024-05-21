# Function to install Python 3
function Install-Python {
    $OS = $null
    if ($IsLinux) {
        $OS = "Linux"
    } elseif ($IsMacOS) {
        $OS = "Mac"
    } elseif ($IsWindows) {
        $OS = "Windows"
    } else {
        $OS = "UNKNOWN"
    }

    Write-Output "Detected OS: $OS"

    if ($OS -eq "Linux") {
        # Assuming Debian-based system; modify as needed for other distros
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    } elseif ($OS -eq "Mac") {
        # Assumes Homebrew is installed
        brew install python3
    } elseif ($OS -eq "Windows") {
        # Download and install Python 3 for Windows
        $pythonInstaller = "$env:TEMP\python-installer.exe"
        Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.9.5/python-3.9.5-amd64.exe" -OutFile $pythonInstaller
        Start-Process -FilePath $pythonInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -NoNewWindow -Wait
        Remove-Item $pythonInstaller
    }
}

# Function to install pip on Windows
function Install-Pip {
    $getPipScript = "$env:TEMP\get-pip.py"
    Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $getPipScript
    python $getPipScript
    Remove-Item $getPipScript
}

# Check if Python 3 is installed
if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    Write-Output "Python 3 could not be found, installing..."
    Install-Python
    Install-Pip
} else {
    Write-Output "Python 3 is already installed."
}

# Default path for the virtual environment
$DefaultVenvPath = ".\.venv"
# Get the directory of the current script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PythonScriptPath = "$ScriptDir\start.py"
$RequirementsPath = "$ScriptDir\requirements.txt"
$env:PYTHONPATH = "$env:PYTHONPATH;$HOME\Downloads\stegAES-main;$HOME\Downloads\stegAES"

# Check if a custom path is provided; if not, use the default
$VenvPath = if ($args.Length -gt 0) { $args[0] } else { $DefaultVenvPath }

# Function to setup virtual environment and install requirements
function Setup-Venv {
    Write-Output "Setting up Python virtual environment at $VenvPath..."
    python3 -m venv $VenvPath
    & "$VenvPath\Scripts\Activate.ps1"
    pip install -r $RequirementsPath
    # Verifying that Flask and Gunicorn are correctly installed and executable paths are available
    Get-Command flask
    Get-Command gunicorn
    & "$VenvPath\Scripts\Deactivate.ps1"
    Write-Output "Virtual environment and dependencies are set up. Flask and Gunicorn paths verified."
}

# Check if the virtual environment directory exists
if (-not (Test-Path $VenvPath)) {
    Setup-Venv
} else {
    Write-Output "Virtual environment already exists at $VenvPath."
}

# Add virtual environment bin to PATH temporarily
$env:PATH = "$VenvPath\Scripts;$env:PATH"

# Activate the virtual environment
& "$VenvPath\Scripts\Activate.ps1"

# Verifying the path for executables again to confirm
Get-Command flask
Get-Command gunicorn

# Run the Python script
python $PythonScriptPath

# Deactivate the virtual environment
& "$VenvPath\Scripts\Deactivate.ps1"

# Optionally: Remove the virtual environment bin from PATH if desired
$env:PATH = $env:PATH -replace [regex]::Escape("$VenvPath\Scripts;"), ""
