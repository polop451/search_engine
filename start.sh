#!/bin/bash

# Navigate to the correct directory
cd "$(dirname "$0")"

# Export PYTHONPATH
export PYTHONPATH=$(pwd)

# Activate conda environment and start server
conda run -n vector-api uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
