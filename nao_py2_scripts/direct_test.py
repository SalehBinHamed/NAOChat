#!/usr/bin/env python2.7
# Simple test script for NAO connection with detailed debugging

import sys
import os
import traceback

# Add SDK paths to Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SDK_DIR = os.path.join(PROJECT_ROOT, "pynaoqi-sdk")

print("Script directory:", SCRIPT_DIR)
print("Project root:", PROJECT_ROOT)
print("SDK directory path:", SDK_DIR)

if os.path.exists(SDK_DIR):
    print("Found NAOqi SDK at:", SDK_DIR)
    sdk_paths = [
        os.path.join(SDK_DIR, "lib", "python2.7", "site-packages"),
        os.path.join(SDK_DIR, "lib"),
        SDK_DIR
    ]
    for p in sdk_paths:
        if os.path.exists(p):
            sys.path.insert(0, p)
            print("Added path:", p)
        else:
            print("Path does not exist:", p)

    # Print entire sys.path to debug
    print("\nFull Python path:")
    for p in sys.path:
        print("-", p)
else:
    print("NAOqi SDK not found at:", SDK_DIR)

# Set environment variable for library path
if os.path.exists(os.path.join(SDK_DIR, "lib")):
    os.environ["DYLD_LIBRARY_PATH"] = os.path.join(SDK_DIR, "lib")
    print("\nSet DYLD_LIBRARY_PATH to:", os.environ["DYLD_LIBRARY_PATH"])
else:
    print("\nCould not set DYLD_LIBRARY_PATH - lib directory not found")

# Get robot IP from command line argument or use default
if len(sys.argv) > 1:
    robot_ip = sys.argv[1]
else:
    robot_ip = "192.168.100.172"  # Default IP
    
print("\nAttempting to connect to NAO at IP:", robot_ip)

try:
    print("Trying to import naoqi module...")
    from naoqi import ALProxy
    print("Successfully imported naoqi module")
    
    print("Attempting to create ALProxy for TextToSpeech...")
    tts = ALProxy("ALTextToSpeech", robot_ip, 9559)
    print("Successfully connected to NAO robot!")
    
    available_languages = tts.getAvailableLanguages()
    print("Available languages:", available_languages)
    current_language = tts.getLanguage()
    print("Current language:", current_language)
    
    # Make the robot say something
    print("Sending test message to NAO...")
    tts.say("Hello, I am connected!")
    print("Test message sent to robot")
    
except ImportError as e:
    print("\nError importing NAOqi module:", e)
    print("Python version:", sys.version)
    print("This usually means the NAOqi Python SDK is not properly installed or not in the Python path")
except Exception as e:
    print("\nError connecting to NAO robot:", e)
    print("Traceback:")
    traceback.print_exc()
    
print("\nTest script completed")