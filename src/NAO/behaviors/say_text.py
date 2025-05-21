#!/usr/bin/env python
# -*- coding: utf-8 -*-
from naoqi import ALProxy
import sys
import time

def main(robot_ip, text):
    try:
        tts = ALProxy("ALTextToSpeech", robot_ip, 9559)
        tts.say(text)
        return True
    except Exception as e:
        print("Error:", e)
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python say_text.py <robot_ip> <text>")
        sys.exit(1)
    
    robot_ip = sys.argv[1]
    text = " ".join(sys.argv[2:])
    main(robot_ip, text)
