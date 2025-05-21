#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
NAO Response Script - Run this in Choregraphe
"""

from naoqi import ALProxy
import time

try:
    # Connect to the robot (localhost when run through Choregraphe)
    tts = ALProxy("ALTextToSpeech", "localhost", 9559)
    
    # Text for NAO to say (from ChatGPT)
    response_text = """"""
    
    # Make NAO speak the response
    print("NAO is saying: " + response_text)
    tts.say(response_text)
    
    print("Speech completed successfully!")
except Exception as e:
    print("Error:", e)
