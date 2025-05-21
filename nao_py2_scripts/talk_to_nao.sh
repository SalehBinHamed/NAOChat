#!/bin/bash
# Simple NAO robot communication script

# Default parameters
NAO_IP="${1:-192.168.100.172}"
MESSAGE="${2:-Hello}"
LANGUAGE="${3:-English}"
VOLUME="${4:-80}"

echo "===== NAO Robot Communication ====="
echo "Robot IP: $NAO_IP"
echo "Message: $MESSAGE"
echo "Language: $LANGUAGE"
echo "Volume: $VOLUME"
echo "=================================="

# Directory setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SDK_DIR="$PROJECT_ROOT/pynaoqi-sdk"

# Create a Python script that communicates with NAO
NAO_SCRIPT="$SCRIPT_DIR/talk_to_nao.py"

cat > "$NAO_SCRIPT" << EOF
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time

# Add the NAOqi SDK to the path
sdk_dir = "$SDK_DIR"
sys.path.insert(0, sdk_dir)
sys.path.insert(0, os.path.join(sdk_dir, "lib"))

try:
    from naoqi import ALProxy
    print("NAOqi module imported successfully")
except ImportError as e:
    print("Error importing NAOqi module: {}".format(e))
    sys.exit(1)

def main():
    robot_ip = "$NAO_IP"
    message = u"$MESSAGE"
    language = "$LANGUAGE"
    volume = $VOLUME
    
    print("Connecting to NAO robot at {}...".format(robot_ip))
    
    try:
        # Connect to the NAO modules
        tts = ALProxy("ALTextToSpeech", robot_ip, 9559)
        audio = ALProxy("ALAudioDevice", robot_ip, 9559)
        
        # Set language if available
        languages = tts.getAvailableLanguages()
        print("Available languages: {}".format(", ".join(languages)))
        
        if language in languages:
            tts.setLanguage(language)
            print("Set language to: {}".format(language))
        else:
            print("Warning: Language {} not available.".format(language))
            print("Available languages: {}".format(", ".join(languages)))
            print("Using robot's current language instead.")
        
        # Set volume
        audio.setOutputVolume(volume)
        print("Set volume to: {}%".format(volume))
        
        # Say the message
        print("Saying message: {}".format(message.encode('utf-8')))
        tts.say(message)
        time.sleep(2)  # Wait for speech to complete
        
        print("Message successfully delivered to NAO!")
        return 0
    except Exception as e:
        print("Error communicating with NAO robot: {}".format(e))
        return 1

if __name__ == "__main__":
    sys.exit(main())
EOF

# Make the script executable
chmod +x "$NAO_SCRIPT"

# Run the script
echo "Connecting to NAO robot at $NAO_IP..."
python2.7 "$NAO_SCRIPT"

if [ $? -eq 0 ]; then
  echo "Communication with NAO robot successful!"
else
  echo "Failed to communicate with NAO robot."
fi