#!/bin/bash

# Enable debugging and print all commands that are executed
set -x

# Exit immediately if a command exits with a non-zero status
set -e

# Remove the existing virtual environment if it exists
if [ -d "venv" ]; then
    rm -rf venv
fi

# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Verify that the virtual environment is activated
which python
which pip

# Upgrade setuptools and wheel
pip install --upgrade setuptools wheel

# Install required packages
pip install fastapi uvicorn python-multipart
pip install git+https://github.com/openai/whisper
pip install sentence-transformers
pip install pinecone-client
pip install python-dotenv
