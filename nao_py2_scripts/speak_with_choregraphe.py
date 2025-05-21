#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple NAO speech script for Choregraphe
Open this file in Choregraphe while connected to NAO
"""

from naoqi import ALProxy
import sys
import time

# The text you want NAO to say
TEXT = "Hello, I am NAO robot. I can now speak through Choregraphe. I will be your assistant powered by ChatGPT."

try:
    # Connect to robot (using localhost when run through Choregraphe)
    print("Connecting to robot...")
    tts = ALProxy("ALTextToSpeech", "localhost", 9559)
    
    # Say the text
    print("Making NAO say: {}".format(TEXT))
    tts.say(TEXT)
    
    print("Speech completed successfully!")
    
except Exception as e:
    print("Error:", e)