#!/bin/bash
# Simple Docker-based NAO communication script with improved error handling

# Parameters
NAO_IP="${1:-192.168.100.172}"
MESSAGE="${2:-Hello, I am NAO robot. Can you hear me now?}"
LANGUAGE="${3:-English}"
VOLUME="${4:-80}"

echo "===== Simple NAO Docker Communication ====="
echo "IP: $NAO_IP"
echo "Message: $MESSAGE"
echo "Language: $LANGUAGE"
echo "Volume: $VOLUME"
echo "========================================"

# First check if the NAO robot is reachable
echo "Checking if NAO is reachable at $NAO_IP..."
if ping -c 1 $NAO_IP > /dev/null 2>&1; then
  echo "NAO robot is reachable!"
else
  echo "ERROR: Cannot reach NAO robot at $NAO_IP"
  echo "Please check that your NAO robot is powered on and connected to the network."
  exit 1
fi

# Create temporary Python script
TMP_SCRIPT="/tmp/nao_talk_$$.py"

cat > "$TMP_SCRIPT" << EOF
#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
import sys
import os
import time
import traceback

# Add paths for NAOqi SDK
SDK_DIR = "/app/pynaoqi-sdk"
sys.path.insert(0, SDK_DIR)
sys.path.insert(0, os.path.join(SDK_DIR, "lib"))
sys.path.insert(0, os.path.join(SDK_DIR, "lib/python2.7/site-packages"))

# Set environment variable for library path
os.environ["LD_LIBRARY_PATH"] = os.path.join(SDK_DIR, "lib")

print("Python version:", sys.version)
print("SDK paths:", sys.path[:3])
print("LD_LIBRARY_PATH:", os.environ.get("LD_LIBRARY_PATH", "Not set"))

try:
    print("Attempting to import naoqi module...")
    from naoqi import ALProxy
    print("Successfully imported naoqi module")
    
    # Connect to NAO
    print("Connecting to NAO at $NAO_IP...")
    tts = ALProxy("ALTextToSpeech", "$NAO_IP", 9559)
    audio = ALProxy("ALAudioDevice", "$NAO_IP", 9559)
    
    # Set language if available
    languages = tts.getAvailableLanguages()
    print("Available languages:", ", ".join(languages))
    
    if "$LANGUAGE" in languages:
        tts.setLanguage("$LANGUAGE")
        print("Set language to: $LANGUAGE")
    else:
        print("Language $LANGUAGE not available")
        print("Using NAO's current language:", tts.getLanguage())
    
    # Set volume
    audio.setOutputVolume($VOLUME)
    print("Set volume to: $VOLUME%")
    
    # Say message
    print("Saying: $MESSAGE")
    tts.say("$MESSAGE")
    time.sleep(2)  # Give time for speech to complete
    print("Message delivered successfully")
    
except ImportError as e:
    print("Error importing NAOqi module:", e)
    print("This usually means the NAOqi SDK is not properly installed or not in the Python path")
    sys.exit(1)
except Exception as e:
    print("Error communicating with NAO robot:", e)
    print("Traceback:")
    traceback.print_exc()
    sys.exit(1)
EOF

# Run Docker container with Python 2.7 and NAOqi support
echo "Running Docker container to communicate with NAO..."

# Pull Python 2.7 image if it doesn't exist
docker pull python:2.7-slim || { echo "Error: Failed to pull Docker image"; exit 1; }

# Install required packages in the container
docker run --rm \
    -v "$TMP_SCRIPT:/app/script.py" \
    -v "$HOME/Desktop/NAOChat/pynaoqi-sdk:/app/pynaoqi-sdk" \
    --network host \
    python:2.7-slim \
    bash -c "
        echo 'Installing required packages...'
        apt-get update && apt-get install -y libssl-dev libffi-dev
        
        echo 'Setting environment variables...'
        export PYTHONPATH=/app/pynaoqi-sdk:/app/pynaoqi-sdk/lib:/app/pynaoqi-sdk/lib/python2.7/site-packages
        export LD_LIBRARY_PATH=/app/pynaoqi-sdk/lib
        
        echo 'Running script...'
        python /app/script.py
    "

# Check if the Docker command succeeded
if [ $? -eq 0 ]; then
    echo "Communication with NAO robot successful!"
else
    echo "Failed to communicate with NAO robot."
    echo "Please check:"
    echo "1. The NAO robot is powered on"
    echo "2. The NAO robot is on the same network as this computer"
    echo "3. The IP address ($NAO_IP) is correct"
    echo "4. The NAOqi SDK is properly installed in the pynaoqi-sdk directory"
fi

# Clean up
rm -f "$TMP_SCRIPT"
echo "Done"