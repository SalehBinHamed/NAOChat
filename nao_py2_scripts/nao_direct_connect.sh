#!/bin/bash
# Comprehensive script to set up and communicate with NAO robot

set -e  # Exit on error

# Default parameters
NAO_IP="${1:-192.168.100.172}"
MESSAGE="${2:-مرحبا}"
LANGUAGE="${3:-Arabic}"
VOLUME="${4:-80}"

echo "==== NAO Robot Direct Communication Setup ====="
echo "Robot IP: $NAO_IP"
echo "Message: $MESSAGE"
echo "Language: $LANGUAGE"
echo "Volume: $VOLUME"
echo "=============================================="

# Check for Python 2.7
if ! command -v python2.7 &> /dev/null; then
  echo "Error: Python 2.7 is required but not found."
  echo "Please install Python 2.7 before continuing."
  exit 1
fi

# Directory setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
SDK_DIR="$PROJECT_ROOT/pynaoqi-sdk"
mkdir -p "$SDK_DIR"

# Check if NAOqi SDK is already downloaded
if [ ! -f "$SDK_DIR/pynaoqi_installed" ]; then
  echo "NAOqi SDK not found in project. Checking if there's a downloadable version..."
  
  # Check if there's a pynaoqi folder in common locations
  # Updated list to include more potential SDK names and locations based on 2.8.6 version
  POSSIBLE_SDK_LOCATIONS=(
    "$HOME/Downloads/pynaoqi-python2.7-2.8.6-mac64"
    "$HOME/Downloads/pynaoqi-python2.7-2.5.7.1-mac64"
    "$HOME/Downloads/pynaoqi-sdk"
    "$HOME/Downloads/pynaoqi"
    "$HOME/Desktop/pynaoqi-python2.7-2.8.6-mac64"
    "$HOME/Desktop/pynaoqi-python2.7-2.5.7.1-mac64"
    "$HOME/Desktop/pynaoqi-sdk"
    "$HOME/Desktop/pynaoqi"
    "$PROJECT_ROOT/../pynaoqi-python2.7-2.8.6-mac64"
    "$PROJECT_ROOT/../pynaoqi-python2.7-2.5.7.1-mac64"
    "$HOME/Documents/pynaoqi-python2.7-2.8.6-mac64"
  )
  
  SDK_FOUND=false
  for location in "${POSSIBLE_SDK_LOCATIONS[@]}"; do
    if [ -d "$location" ]; then
      echo "Found NAOqi SDK at $location"
      echo "Creating symlink to the SDK..."
      ln -sf "$location"/* "$SDK_DIR/"
      touch "$SDK_DIR/pynaoqi_installed"
      SDK_FOUND=true
      break
    fi
  done
  
  if [ "$SDK_FOUND" = false ]; then
    echo "Let's search the entire Downloads and Desktop folders for any SDK-like directories..."
    FOUND_SDK=$(find "$HOME/Downloads" "$HOME/Desktop" -type d -name "pynaoqi*" -o -name "*naoqi*" 2>/dev/null | head -1)
    
    if [ -n "$FOUND_SDK" ]; then
      echo "Found potential NAOqi SDK at: $FOUND_SDK"
      echo "Creating symlink to the SDK..."
      ln -sf "$FOUND_SDK"/* "$SDK_DIR/"
      touch "$SDK_DIR/pynaoqi_installed"
      SDK_FOUND=true
    fi
  fi
  
  if [ "$SDK_FOUND" = false ]; then
    echo "==================== ATTENTION ===================="
    echo "NAOqi SDK not found on your system."
    echo ""
    echo "I see you're downloading it from the Aldebaran/SoftBank website."
    echo "Please extract the downloaded SDK to one of these locations:"
    echo "- $HOME/Downloads/pynaoqi-python2.7-2.8.6-mac64"
    echo "- $HOME/Desktop/pynaoqi-python2.7-2.8.6-mac64"
    echo ""
    echo "Or specify the path where you extracted it:"
    echo "  SDK_PATH=/path/to/extracted/sdk $0"
    echo ""
    echo "Then run this script again."
    echo "=================================================="
    exit 1
  fi
fi

# Handle manually specified SDK path
if [ -n "$SDK_PATH" ] && [ -d "$SDK_PATH" ]; then
  echo "Using manually specified SDK path: $SDK_PATH"
  ln -sf "$SDK_PATH"/* "$SDK_DIR/"
  touch "$SDK_DIR/pynaoqi_installed"
fi

# Create a Python script that communicates with NAO
echo "Creating NAO communication script..."
NAO_SCRIPT="$SCRIPT_DIR/test_nao_speech.py"

cat > "$NAO_SCRIPT" << EOF
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time

# Add the NAOqi SDK to the path
sdk_dir = "$SDK_DIR"
if os.path.exists(sdk_dir):
    sys.path.insert(0, sdk_dir)
    # Also add lib directory which might contain the actual Python modules
    lib_dir = os.path.join(sdk_dir, "lib")
    if os.path.exists(lib_dir):
        sys.path.insert(0, lib_dir)
    # For Mac, there might be a specific path for the compiled modules
    mac_dir = os.path.join(sdk_dir, "lib", "python2.7", "site-packages")
    if os.path.exists(mac_dir):
        sys.path.insert(0, mac_dir)
    # Add additional potential locations based on SDK version
    mac_dir2 = os.path.join(sdk_dir, "lib", "python27.zip")
    if os.path.exists(mac_dir2):
        sys.path.insert(0, mac_dir2)

# Try to import naoqi
try:
    from naoqi import ALProxy
    print("NAOqi module imported successfully")
except ImportError as e:
    print("Error importing NAOqi module: {}".format(e))
    print("\nPython path:")
    for p in sys.path:
        print("  - {}".format(p))
    print("\nSearching for NAOqi module files...")
    import glob
    for p in sys.path:
        if os.path.exists(p):
            print("Checking {}:".format(p))
            for pattern in ["*naoqi*", "*alcommon*", "_inaoqi*"]:
                files = glob.glob(os.path.join(p, pattern))
                for f in files:
                    print("  Found: {}".format(f))
    sys.exit(1)

def main():
    robot_ip = "$NAO_IP"
    message = u"$MESSAGE"
    language = "$LANGUAGE"
    volume = $VOLUME
    
    print("Connecting to NAO robot at {}...".format(robot_ip))
    
    try:
        # First check if robot is reachable by pinging
        import subprocess
        ping_cmd = ["ping", "-c", "1", "-W", "2", robot_ip]
        try:
            if subprocess.call(ping_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE) != 0:
                print("Warning: NAO robot at {} doesn't respond to ping".format(robot_ip))
                print("Will still try to connect...")
        except Exception:
            print("Could not ping robot, continuing anyway...")
        
        # Connect to the NAO modules
        tts = ALProxy("ALTextToSpeech", robot_ip, 9559)
        audio = ALProxy("ALAudioDevice", robot_ip, 9559)
        
        # Get available languages
        languages = tts.getAvailableLanguages()
        print("Available languages: {}".format(", ".join(languages)))
        
        # Set language if available
        if language in languages:
            tts.setLanguage(language)
            print("Set language to: {}".format(language))
        else:
            print("Warning: Language {} not available.".format(language))
            print("Using robot's current language instead.")
        
        # Set volume
        audio.setOutputVolume(volume)
        print("Set volume to: {}%".format(volume))
        
        # Say the message
        print("Saying message: {}".format(message.encode('utf-8')))
        tts.say(message)
        print("Message delivered to NAO!")
        
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
echo "Running NAO communication script with Python 2.7..."
python2.7 "$NAO_SCRIPT"
EXIT_CODE=$?

# Check result
if [ $EXIT_CODE -eq 0 ]; then
  echo "Successfully communicated with NAO robot!"
else
  echo "Failed to communicate with NAO robot."
  echo ""
  echo "Troubleshooting steps:"
  echo "1. Make sure your NAO robot is powered on"
  echo "2. Confirm the robot is on the same network as your computer"
  echo "3. Verify the IP address is correct (current: $NAO_IP)"
  echo "4. Check if you can ping the robot: ping $NAO_IP"
  echo ""
  echo "If you know where you extracted the SDK, you can specify it directly:"
  echo "  SDK_PATH=/path/to/extracted/sdk $0"
fi

exit $EXIT_CODE