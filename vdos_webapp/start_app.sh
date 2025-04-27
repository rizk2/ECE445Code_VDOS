#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1 || { echo >&2 "Error: $1 is not installed. Please install it and try again."; exit 1; }
}

python_library_exists() {
    python3.13 -c "import $1" >/dev/null 2>&1 || { echo >&2 "Error: Python library '$1' is not installed. Please install it and try again."; exit 1; }
}

# Check the python dependencies
command_exists python3.13
command_exists uvicorn
python_library_exists librosa
python_library_exists numpy
python_library_exists parselmouth
python_library_exists soundfile
python_library_exists matplotlib
python_library_exists fastapi

# Check the javascript dependencies
command_exists npm

# Kill any existing Python or Uvicorn processes
echo "Killing any existing Python or Uvicorn processes..."
pkill -f uvicorn || echo "No Uvicorn processes found."
pkill -f python3.13 || echo "No Python processes found."

# Kill processes using port 8000
echo "Checking for processes using port 8000..."
lsof -ti :8000 | xargs kill -9 || echo "No processes using port 8000."

# Start the backend
echo "Starting the backend..."
cd backend || exit
python3.13 -m uvicorn main:app --reload &
BACKEND_PID=$!

# Start the frontend
echo "Starting the frontend..."
cd ../react-frontend || exit
npm install
npm start

# Cleanup: Kill the backend process when the script is terminated
trap "kill $BACKEND_PID" EXIT