#!/bin/bash

# Set resource limits
ulimit -t 30  # CPU time limit (30 seconds)
ulimit -m 512000  # Memory limit (512MB)
ulimit -f 1024  # File size limit (1MB)

# Execute the Python code
python3 /app/code/script.py 