#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script to directly communicate with NAO robot using NAOqi API
Compatible with Python 2.7 and NAOqi SDK
"""

import sys
import time
import os

# Try to import NAOqi modules
try:
    from naoqi import ALProxy
except ImportError:
    # If pynaoqi SDK is in a custom location, try to add it to path
    pynaoqi_path = os.path.join(os.path.dirname(__file__), '..', 'pynaoqi')
    if os.path.exists(pynaoqi_path):
        sys.path.append(pynaoqi_path)
        try:
            from naoqi import ALProxy
            print("Using NAOqi SDK from: {}".format(pynaoqi_path))
        except ImportError:
            print("Error: Cannot import naoqi module.")
            print("Make sure the NAOqi SDK is properly installed.")
            sys.exit(1)
    else:
        print("Error: NAOqi SDK not found in {}".format(pynaoqi_path))
        print("Please download the SDK from SoftBank Robotics website.")
        sys.exit(1)


def main():
    # Default values
    robot_ip = "192.168.100.172"  # Default IP
    message = u"تم الاتصال بنجاح"  # Default message: Connection successful in Arabic
    language = "Arabic"  # Default language
    volume = 100  # Default volume (0-100)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        robot_ip = sys.argv[1]
    if len(sys.argv) > 2:
        message = unicode(sys.argv[2], "utf-8")
    if len(sys.argv) > 3:
        language = sys.argv[3]
    if len(sys.argv) > 4:
        try:
            volume = int(sys.argv[4])
            if volume < 0 or volume > 100:
                print("Warning: Volume should be between 0-100, setting to 100")
                volume = 100
        except ValueError:
            print("Warning: Invalid volume value, using default 100")
            volume = 100
    
    # Print connection information
    print("Connecting to NAO robot:")
    print("  - IP: {}".format(robot_ip))
    print("  - Message: {}".format(message.encode('utf-8')))
    print("  - Language: {}".format(language))
    print("  - Volume: {}".format(volume))
    
    # Try to connect to the robot
    try:
        # Create proxies to ALTextToSpeech and ALAudioDevice modules
        tts = ALProxy("ALTextToSpeech", robot_ip, 9559)
        audio = ALProxy("ALAudioDevice", robot_ip, 9559)
        
        # Get available languages and check if requested language is available
        available_languages = tts.getAvailableLanguages()
        print("Available languages: {}".format(", ".join(available_languages)))
        
        if language in available_languages:
            tts.setLanguage(language)
            print("Set language to: {}".format(language))
        else:
            print("Warning: Language '{}' not available. Using default.".format(language))
        
        # Set volume
        audio.setOutputVolume(volume)
        print("Set volume to: {}".format(volume))
        
        # Say the message
        print("Saying message...")
        tts.say(message)
        time.sleep(1)  # Wait for the speech to complete
        
        print("Message delivered successfully.")
        return 0
        
    except Exception as e:
        print("Error connecting to NAO robot: {}".format(str(e)))
        print("Please check:")
        print("1. NAO robot is powered on")
        print("2. NAO robot is connected to the network")
        print("3. The IP address is correct")
        print("4. NAO robot's SSH port (22) is not blocked")
        return 1


if __name__ == "__main__":
    sys.exit(main())