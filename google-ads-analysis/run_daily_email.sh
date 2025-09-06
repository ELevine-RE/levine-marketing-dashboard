#!/bin/bash
# Daily Email Runner Script
# This script activates the virtual environment and runs the daily email

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Activate virtual environment
source .venv/bin/activate

# Run the daily email script
python daily_email_config.py "$@"

# Deactivate virtual environment
deactivate
