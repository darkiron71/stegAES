#!/bin/bash

# Default path for the virtual environment
DEFAULT_VENV_PATH="./.venv"
# Get the directory of the current script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PYTHON_SCRIPT_PATH="$SCRIPT_DIR/start.py"
REQUIREMENTS_PATH="$SCRIPT_DIR/requirements.txt"

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
