#!/bin/bash

# Direct NAO Robot Connection Script
# This script uses SSH to directly connect to your NAO robot and send a message

# Configuration
NAO_IP="${1:-192.168.100.172}"  # Use the first argument or default to this IP
MESSAGE="${2:-تم الاتصال بنجاح}"  # Use the second argument or default to "Connected successfully" in Arabic
NAO_USER="nao"                  # Default username on NAO robot
NAO_PASSWORD="nao"              # Default password on NAO robot

echo "Connecting to NAO robot at $NAO_IP..."
echo "Sending message: $MESSAGE"

# Use sshpass to automate password entry (install if needed)
if ! command -v sshpass &> /dev/null; then
    echo "sshpass not found. Installing..."
    brew install sshpass
fi

# Prepare a Python script to execute on the NAO robot
TEMP_SCRIPT=$(mktemp)
cat > "$TEMP_SCRIPT" << EOF
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from naoqi import ALProxy

try:
    tts = ALProxy("ALTextToSpeech", "localhost", 9559)
    audio = ALProxy("ALAudioDevice", "localhost", 9559)
    
    # Set language to Arabic
    tts.setLanguage("Arabic")
    
    # Set volume to maximum
    audio.setOutputVolume(100)
    
    # Say the message
    tts.say('$MESSAGE')
    
    print("Message delivered successfully!")
except Exception as e:
    print("Error: " + str(e))
EOF

# Send the script to the NAO and execute it
echo "Sending script to NAO robot..."
sshpass -p "$NAO_PASSWORD" scp -o StrictHostKeyChecking=no "$TEMP_SCRIPT" "$NAO_USER@$NAO_IP:/tmp/speak.py"
sshpass -p "$NAO_PASSWORD" ssh -o StrictHostKeyChecking=no "$NAO_USER@$NAO_IP" "python /tmp/speak.py"

# Clean up
rm -f "$TEMP_SCRIPT"
echo "Done."