#!/bin/bash

# Check for exactly one argument
if [ $# -ne 1 ]; then
  echo "Usage: $0 <python_script_path>" >&2
  exit 1
fi
PYTHON_SCRIPT="$1"

# Determine script directory
SCRIPT_DIR=$(dirname "$(realpath "$0" 2>/dev/null || readlink -f "$0" 2>/dev/null || echo "$0")")

# Ensure write permissions for script directory
chmod u+w "$SCRIPT_DIR" || {
  echo "Error: Could not set write permissions for $SCRIPT_DIR" >&2
  exit 1
}

# Create temporary project directory
TEMP_DIR="$SCRIPT_DIR/.temp/$(date +%s)-$$"
mkdir -p "$TEMP_DIR" || {
  echo "Error: Could not create temporary directory $TEMP_DIR" >&2
  exit 1
}
chmod u+w "$TEMP_DIR" || {
  echo "Error: Could not set write permissions for $TEMP_DIR" >&2
  exit 1
}
PROJECT_DIR="$TEMP_DIR"
echo "Project directory: $PROJECT_DIR"
echo "Python script to run: $PYTHON_SCRIPT"

# Copy files to project directory, excluding files and folders starting with .
shopt -s dotglob
for item in "$SCRIPT_DIR"/*; do
  basename=$(basename "$item")
  if [[ "$basename" == .* ]]; then
    continue
  fi
  cp -r "$item" "$PROJECT_DIR"/ || {
    echo "Error: Failed to copy $item to $PROJECT_DIR" >&2
    exit 1
  }
done
shopt -u dotglob

# Change to project directory
cd "$PROJECT_DIR" || {
  echo "Error: Could not change to directory $PROJECT_DIR" >&2
  exit 1
}

# Remove existing virtual environment if present
if [ -d ".venv" ]; then
  echo "Removing existing .venv directory..."
  rm -rf ".venv"
else
  echo ".venv directory not present, continuing..."
fi

# Install uv locally
echo "Installing uv locally..."
if ! curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=$(pwd) sh; then
  echo "Error: Failed to install uv" >&2
  exit 1
fi

export PATH="$PROJECT_DIR:$PATH"

# Verify uv is available
if ! command -v uv >/dev/null 2>&1; then
  echo "Error: uv command not found after installation" >&2
  exit 1
fi

# Create virtual environment
echo "Creating new virtual environment..."
uv venv || {
  echo "Error: Failed to create virtual environment" >&2
  exit 1
}
if [ ! -d ".venv" ]; then
  echo "Error: Virtual environment directory .venv not found" >&2
  exit 1
fi

# Activate the virtual environment
echo "Activating the virtual environment..."
source .venv/bin/activate || {
  echo "Error: Failed to activate virtual environment" >&2
  exit 1
}

# Sync dependencies using uv
echo "Syncing dependencies with uv..."
if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
  uv sync || {
    echo "Error: Failed to sync dependencies with uv" >&2
    exit 1
  }
else
  echo "Warning: No pyproject.toml or requirements.txt found, skipping dependency sync" >&2
fi

# Run the specified Python script
echo "Running $PYTHON_SCRIPT..."
uv run "$PYTHON_SCRIPT" || {
  echo "Error: Failed to run $PYTHON_SCRIPT" >&2
  exit 1
}

# Remove the temporary project directory on exit
rm -rf "$PROJECT_DIR"