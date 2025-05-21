#!/bin/bash
# Script to run the NAO communicator Docker container

# Configuration
NAO_IP="${1:-192.168.100.172}"
MESSAGE="${2:-تم الاتصال بنجاح}"
LANGUAGE="${3:-Arabic}"
VOLUME="${4:-100}"

echo "==== NAO Robot Communication Docker ====="
echo "Robot IP: $NAO_IP"
echo "Message: $MESSAGE"
echo "Language: $LANGUAGE"
echo "Volume: $VOLUME"
echo "========================================"

# Check if Docker is running
if ! docker info &>/dev/null; then
    echo "Error: Docker is not running."
    echo "Please start Docker Desktop and try again."
    exit 1
fi

# Check if the nao-communicator image exists
if ! docker image inspect nao-communicator &>/dev/null; then
    echo "Docker image 'nao-communicator' not found."
    echo "Building the image now..."
    
    # Build the image
    if ! docker build -t nao-communicator .; then
        echo "Error: Failed to build Docker image."
        exit 1
    fi
    
    echo "Docker image built successfully."
fi

# Run the Docker container to communicate with NAO
echo "Starting communication with NAO..."
echo "This might take a moment if this is the first run..."

docker run --rm \
    --network host \
    nao-communicator "$NAO_IP" "$MESSAGE" "$LANGUAGE" "$VOLUME"

# Check if the command succeeded
if [ $? -eq 0 ]; then
    echo "Command executed successfully!"
else
    echo "Error communicating with NAO."
    echo "This might be because:"
    echo "1. The NAO robot is not powered on"
    echo "2. The NAO robot is not on the same network as your computer"
    echo "3. The IP address is incorrect"
    echo ""
    echo "Try running the find_nao.sh script to locate your NAO robot."
fi
