#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time

# Add the NAOqi SDK to the path with better diagnostic information
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sdk_dir = os.path.join(project_root, "pynaoqi-sdk")

print("SDK directory: {}".format(sdk_dir))

# Add more paths that might contain the NAOqi module
potential_paths = [
    sdk_dir,
    os.path.join(sdk_dir, "lib"),
    os.path.join(sdk_dir, "lib", "python2.7", "site-packages"),
]

for p in potential_paths:
    if os.path.exists(p):
        sys.path.insert(0, p)
        print("Added path: {}".format(p))

# Set environment variable for dynamic libraries
if os.path.exists(os.path.join(sdk_dir, "lib")):
    os.environ["DYLD_LIBRARY_PATH"] = os.path.join(sdk_dir, "lib")
    print("Set DYLD_LIBRARY_PATH to: {}".format(os.environ["DYLD_LIBRARY_PATH"]))

print("Current sys.path:")
for p in sys.path:
    print("  - {}".format(p))

try:
    print("Attempting to import naoqi module...")
    import naoqi
    print("Successfully imported naoqi module")
    print("NAOqi module location: {}".format(naoqi.__file__))
    from naoqi import ALProxy
    print("Successfully imported ALProxy")
except ImportError as e:
    print("Error importing NAOqi module: {}".format(e))
    print("Python version: {}".format(sys.version))
    
    # Try to find naoqi.py manually
    for root, dirs, files in os.walk(sdk_dir):
        if "naoqi.py" in files:
            print("Found naoqi.py at: {}".format(root))
    
    sys.exit(1)

def main():
    robot_ip = "192.168.100.172"
    message = u"Hello, this is a test message"
    language = "English"
    volume = 80
    
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
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
