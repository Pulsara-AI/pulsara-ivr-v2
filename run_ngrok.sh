#!/bin/bash

# Run ngrok to expose the Pulsara IVR v2 application to the internet

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null
then
    echo "ngrok could not be found. Please install ngrok and try again."
    echo "Visit https://ngrok.com/download for installation instructions."
    exit 1
fi

# Get the port from config.py
PORT=$(grep -o 'PORT = [0-9]*' config/settings.py | awk '{print $3}')

# If PORT is not found, use default port 8000
if [ -z "$PORT" ]; then
    PORT=8000
fi

echo "Starting ngrok on port $PORT..."
ngrok http $PORT
