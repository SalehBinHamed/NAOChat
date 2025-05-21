#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time

# Add the NAOqi SDK to the path
sdk_dir = "/Users/yh/Desktop/NAOChat/pynaoqi-sdk"
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
    robot_ip = "192.168.100.172"
    message = u"Hello"
    language = "English"
    volume = 80
    
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
