#!/bin/bash

# Create logs directory if it doesn't exist
mkdir -p logs

# Record start time
echo "Starting Stock Alert Application at $(date)"

# Start the Flask server in the background
python server.py &
SERVER_PID=$!

# Check if server started successfully
if [ $? -eq 0 ]; then
    echo "Server started with PID: $SERVER_PID"
    echo "Access the application at http://localhost:5000"
    echo "Press Ctrl+C to stop the server"
else
    echo "Error: Failed to start the server"
    exit 1
fi

# Wait for user to press Ctrl+C
trap "kill $SERVER_PID; echo 'Server stopped'; exit 0" INT
wait $SERVER_PID