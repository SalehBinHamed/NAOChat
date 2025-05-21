#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Simple NAO control script compatible with Choregraphe
Save this as a Python script in Choregraphe and run it while connected to NAO
"""

# Import NAOqi libraries
from naoqi import ALProxy
import sys
import time

# Connect to robot (local connection when run through Choregraphe)
try:
    # When run through Choregraphe, use localhost
    tts = ALProxy("ALTextToSpeech", "localhost", 9559)
    motion = ALProxy("ALMotion", "localhost", 9559)
    posture = ALProxy("ALRobotPosture", "localhost", 9559)
    leds = ALProxy("ALLeds", "localhost", 9559)
    
    # Test basic movement and speech
    tts.say("Hello! I am NAO. I will now demonstrate some movements.")
    time.sleep(1)
    
    # Stand up
    print("Making NAO stand up...")
    posture.goToPosture("Stand", 0.8)
    time.sleep(2)
    
    # Wave right arm
    print("Waving right arm...")
    motion.setAngles("RShoulderPitch", 0.5, 0.2)
    motion.setAngles("RShoulderRoll", -0.3, 0.2)
    time.sleep(1)
    motion.setAngles("RElbowRoll", 1.0, 0.2)
    time.sleep(0.5)
    
    # Wave hand back and forth
    for i in range(3):
        motion.setAngles("RElbowYaw", -0.5, 0.2)
        time.sleep(0.5)
        motion.setAngles("RElbowYaw", 0.5, 0.2)
        time.sleep(0.5)
    
    # Return to neutral position
    print("Returning to neutral position...")
    motion.setAngles("RShoulderPitch", 1.0, 0.2)
    motion.setAngles("RShoulderRoll", 0.0, 0.2)
    motion.setAngles("RElbowRoll", 0.0, 0.2)
    motion.setAngles("RElbowYaw", 0.0, 0.2)
    time.sleep(1)
    
    # Blink eyes
    print("Blinking eyes...")
    leds.fadeRGB("FaceLeds", 0x00FF00, 0.5) # Green
    time.sleep(1)
    leds.fadeRGB("FaceLeds", 0x0000FF, 0.5) # Blue
    time.sleep(1)
    leds.fadeRGB("FaceLeds", 0xFFFFFF, 0.5) # White (default)
    
    # Say goodbye
    tts.say("Thank you for watching my demonstration!")
    
    print("Script executed successfully!")
    
except Exception as e:
    print("Error:", e)