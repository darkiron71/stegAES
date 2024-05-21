#!/bin/bash

# Function to install Python 3
install_python() {
    # Detect the platform (similar to $OSTYPE)
    UNAME="$(uname -s)"
    case "${UNAME}" in
        Linux*)     OS=Linux;;
        Darwin*)    OS=Mac;;
        CYGWIN*|MINGW*|MSYS*|MINGW*) OS=Windows;;
        *)          OS="UNKNOWN:${UNAME}"
    esac

    echo "Detected OS: ${OS}"

    if [ "$OS" = "Linux" ]; then
        # Assuming Debian-based system; modify as needed for other distros
        sudo apt-get update
        sudo apt-get install -y python3 python3-pip
    elif [ "$OS" = "Mac" ]; then
        # Assumes Homebrew is installed
        brew install python3
    elif [ "$OS" = "Windows" ]; then
        # Installing Python on Windows via a script might require more steps or admin privileges
        echo "Please install Python 3 from https://www.python.org or enable the Windows Subsystem for Linux (WSL) and install Python through a Linux distribution."
    fi
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 could not be found, installing..."
    install_python
else
    echo "Python 3 is already installed."
fi

# Default path for the virtual environment
DEFAULT_VENV_PATH="./.venv"
# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_SCRIPT_PATH="$SCRIPT_DIR/start.py"
REQUIREMENTS_PATH="$SCRIPT_DIR/requirements.txt"
export PYTHONPATH=$PYTHONPATH:$HOME/Downloads/stegAES-main
export PYTHONPATH=$PYTHONPATH:$HOME/Downloads/stegAES

# Check if a custom path is provided; if not, use the default
VENV_PATH="${1:-$DEFAULT_VENV_PATH}"

# Function to setup virtual environment and install requirements
setup_venv() {
    echo "Setting up Python virtual environment at $VENV_PATH..."
    python3 -m venv "$VENV_PATH"
    source "$VENV_PATH/bin/activate"
    pip install -r "$REQUIREMENTS_PATH"
    # Verifying that Flask and Gunicorn are correctly installed and executable paths are available
    which flask
    which gunicorn
    deactivate
    echo "Virtual environment and dependencies are set up. Flask and Gunicorn paths verified."
}

# Check if the virtual environment directory exists
if [ ! -d "$VENV_PATH" ]; then
    setup_venv
else
    echo "Virtual environment already exists at $VENV_PATH."
fi

# Add virtual environment bin to PATH temporarily
export PATH="$VENV_PATH/bin:$PATH"

# Activate the virtual environment
source "$VENV_PATH/bin/activate"

# Verifying the path for executables again to confirm
which flask
which gunicorn

# Run the Python script
python "$PYTHON_SCRIPT_PATH"

# Deactivate the virtual environment
deactivate

# Optionally: Remove the virtual environment bin from PATH if desired
export PATH=$(echo "$PATH" | sed -e "s;$VENV_PATH/bin:;;")
