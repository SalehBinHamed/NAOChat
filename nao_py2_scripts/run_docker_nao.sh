#!/bin/bash

# This script builds and runs a Docker container for NAO robot connection
# Usage: ./run_docker_nao.sh <robot_ip> <language> <volume> [message_file]

set -e  # Exit on error

# Set defaults
ROBOT_IP="${1:-192.168.100.172}"
LANGUAGE="${2:-Arabic}"
VOLUME="${3:-100}"
MESSAGE_FILE="${4:-}"  # Optional path to a file containing the message to send

# Directory paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
NAO_DIR="$ROOT_DIR/src/NAO"
PYNAOQI_DIR="$HOME/Desktop/pynaoqi"
CHOREO_DIR="$HOME/Desktop/choregrapher"

# Check if NAO directories exist
if [ ! -d "$PYNAOQI_DIR" ]; then
  echo "Warning: pynaoqi directory not found at $PYNAOQI_DIR"
  echo "Creating empty directory for testing"
  mkdir -p "$PYNAOQI_DIR"
fi

if [ ! -d "$CHOREO_DIR" ]; then
  echo "Warning: choregrapher directory not found at $CHOREO_DIR"
  echo "Creating empty directory for testing" 
  mkdir -p "$CHOREO_DIR"
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
  echo "Error: Docker is not running or not accessible"
  exit 1
fi

# Check if image exists, build only if it doesn't exist
if ! docker image inspect nao-robot > /dev/null 2>&1; then
  echo "Building Docker image for NAO robot connection..."
  docker build -t nao-robot -f "$SCRIPT_DIR/Dockerfile" "$SCRIPT_DIR" || {
    echo "Docker build failed!"
    exit 1
  }
else
  echo "Using existing Docker image nao-robot"
fi

# Read the message from file if provided
MESSAGE=""
if [ -n "$MESSAGE_FILE" ] && [ -f "$MESSAGE_FILE" ]; then
  MESSAGE=$(cat "$MESSAGE_FILE")
  echo "Message to send: $MESSAGE"
else
  echo "No message file provided or file not found"
  exit 1
fi

# Create a Python script that will directly use NAOTalkerPy2.py
TMP_SCRIPT=$(mktemp)
cat > "$TMP_SCRIPT" << EOF
#!/usr/bin/env python
import sys
import time
from naoqi import ALProxy

# Try to connect to the robot
try:
    tts = ALProxy("ALTextToSpeech", "$ROBOT_IP", 9559)
    audio = ALProxy("ALAudioDevice", "$ROBOT_IP", 9559)
    
    # Set language and volume
    if "$LANGUAGE" in tts.getAvailableLanguages():
        tts.setLanguage("$LANGUAGE")
    else:
        print("Language $LANGUAGE not available, using English")
        tts.setLanguage("English")
    
    audio.setOutputVolume($VOLUME)
    
    # Say the message
    print("Saying: $MESSAGE")
    tts.say("$MESSAGE")
    time.sleep(2)  # Give time for speech to complete
    
except Exception as e:
    print("Error connecting to NAO robot: " + str(e))
    sys.exit(1)
EOF

chmod +x "$TMP_SCRIPT"

# Run Docker container with a timeout
echo "Connecting to NAO robot at $ROBOT_IP with language $LANGUAGE and volume $VOLUME"

# Add compatibility for macOS
timeout_command() {
  if command -v timeout &> /dev/null; then
    timeout "$@"
  else
    # On macOS, use gtimeout from coreutils if available
    if command -v gtimeout &> /dev/null; then
      gtimeout "$@"
    else
      # Fallback - run without timeout
      echo "Warning: timeout/gtimeout command not found. Running without timeout protection."
      shift  # Remove the first argument (timeout duration)
      "$@"   # Run the command without timeout
    fi
  fi
}

# Use timeout_command function to limit execution time to 20 seconds
timeout_command 20 docker run --rm -it --network=host \
  -v "$NAO_DIR:/app/src" \
  -v "$PYNAOQI_DIR:/app/pynaoqi" \
  -v "$CHOREO_DIR:/app/choregrapher" \
  -v "$TMP_SCRIPT:/app/nao_speech.py" \
  nao-robot \
  python /app/nao_speech.py || {
    echo "Docker container timed out or failed"
  }

# Clean up temporary script
rm -f "$TMP_SCRIPT"

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

# If you have the NAOqi SDK downloaded, specify the path here
NAOQI_SDK_PATH=~/Downloads/pynaoqi-python2.7-2.5.7.1-mac64

# Check if SDK exists
if [ -d "$NAOQI_SDK_PATH" ]; then
    echo "Found NAOqi SDK at $NAOQI_SDK_PATH"
    MOUNT_OPTION="-v $NAOQI_SDK_PATH:/app/pynaoqi"
else
    echo "NAOqi SDK not found at $NAOQI_SDK_PATH"
    echo "We'll try to continue without the SDK, but this might not work."
    echo "If this fails, please download the SDK from:"
    echo "https://developer.softbankrobotics.com/nao6/naoqi-developer-guide/sdks/python-sdk"
    MOUNT_OPTION=""
fi

# Run the Docker container to communicate with NAO
echo "Starting communication with NAO..."
docker run --rm $MOUNT_OPTION nao-communicator "$NAO_IP" "$MESSAGE" "$LANGUAGE" "$VOLUME"

# Check if the command succeeded
if [ $? -eq 0 ]; then
    echo "Command executed successfully!"
else
    echo "Error communicating with NAO."
    echo "This might be because:"
    echo "1. The NAO robot is not powered on"
    echo "2. The NAO robot is not on the same network as your computer"
    echo "3. The IP address is incorrect"
    echo "4. You don't have the NAOqi SDK installed"
    echo ""
    echo "If you have the NAOqi SDK, please edit this script to set the correct path."
    echo "If you don't have the NAOqi SDK, you can download it from:"
    echo "https://developer.softbankrobotics.com/nao6/naoqi-developer-guide/sdks/python-sdk"
fi