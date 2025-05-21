#!/bin/bash
# Simple direct NAO robot communication script

# Default parameters
NAO_IP="${1:-192.168.100.172}"
MESSAGE="${2:-مرحبا}"
LANGUAGE="${3:-Arabic}"
VOLUME="${4:-80}"

echo "==== Direct NAO Robot Communication ====="
echo "Robot IP: $NAO_IP"
echo "Message: $MESSAGE"
echo "Language: $LANGUAGE"
echo "Volume: $VOLUME"
echo "========================================"

# Paths
NAO_SCRIPT_PATH="/Users/yh/Desktop/NAOChat/src/NAO/NAOTalkerPy2.py"

# Check if Python 2.7 is installed
if ! command -v python2.7 &> /dev/null; then
  echo "Python 2.7 not found. Trying with 'python'..."
  PYTHON_CMD="python"
else
  PYTHON_CMD="python2.7"
fi

# Check if the script exists
if [ ! -f "$NAO_SCRIPT_PATH" ]; then
  echo "Error: NAO script not found at $NAO_SCRIPT_PATH"
  exit 1
fi

# Create a temporary script that uses NAOTalkerPy2.py
TMP_SCRIPT=$(mktemp)
cat > "$TMP_SCRIPT" << EOF
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import time

# Add the NAO directory to the path
sys.path.append(os.path.dirname("$NAO_SCRIPT_PATH"))

try:
    from naoqi import ALProxy
    
    # Connect to the NAO robot
    ip = "$NAO_IP"
    
    try:
        tts = ALProxy("ALTextToSpeech", ip, 9559)
        audio = ALProxy("ALAudioDevice", ip, 9559)
        
        # Set language and volume
        tts.setLanguage("$LANGUAGE")
        audio.setOutputVolume($VOLUME)
        
        # Say the message
        message = u"$MESSAGE"
        print("Saying message: {0}".format(message.encode('utf-8')))
        tts.say(message)
        time.sleep(2)  # Wait for speech to complete
        
        print("Message successfully delivered to NAO robot!")
        
    except Exception as e:
        print("Error connecting to NAO robot: {0}".format(str(e)))
        sys.exit(1)
        
except ImportError:
    print("Error: Could not import naoqi module.")
    print("Make sure you have the correct Python environment with NAOqi SDK.")
    sys.exit(1)
EOF

# Make the script executable
chmod +x "$TMP_SCRIPT"

# Run the script
echo "Connecting to NAO robot at $NAO_IP..."
$PYTHON_CMD "$TMP_SCRIPT"
EXIT_CODE=$?

# Clean up
rm -f "$TMP_SCRIPT"

# Check exit code
if [ $EXIT_CODE -eq 0 ]; then
  echo "Communication with NAO robot successful!"
else
  echo "Failed to communicate with NAO robot."
  echo "Please check if:"
  echo "1. NAO robot is powered on"
  echo "2. NAO robot is on the same network (ping $NAO_IP)"
  echo "3. NAOqi SDK is properly installed for Python 2.7"
  echo ""
  echo "For debugging, try running: ping $NAO_IP"
fi

exit $EXIT_CODE