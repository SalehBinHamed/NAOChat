#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
import time

# Fix import path for Talker class
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Talker import Talker

class ChoregrapheTalker(Talker):
    """
    A talker class that uses Choregraphe to control NAO
    This approach requires Choregraphe to be connected to NAO
    """
    
    def __init__(self, ip: str, language: str = "en", sleep_len: float = 0.03, stand=False, volume: int = 80):
        super().__init__(language=language)
        self.ip = ip
        self.sleep_len = sleep_len
        self.volume = volume
        self.standing = stand
        
        print(f"[CHOREGRAPHE NAO] Setting up connection to NAO at IP: {ip}")
        print(f"[CHOREGRAPHE NAO] Language: {language}")
        print(f"[CHOREGRAPHE NAO] Volume: {volume}")
        print(f"[CHOREGRAPHE NAO] Using Choregraphe to control NAO")
        print(f"[CHOREGRAPHE NAO] Make sure Choregraphe is running and connected to your NAO at {ip}")
        
        # Create the behaviors directory if it doesn't exist
        self.behaviors_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "behaviors")
        if not os.path.exists(self.behaviors_dir):
            os.makedirs(self.behaviors_dir)
            
        # Create a simple say behavior
        self.say_script_path = os.path.join(self.behaviors_dir, "say_text.py")
        with open(self.say_script_path, "w") as f:
            f.write('''#!/usr/bin/env python
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
''')
        
        # Make the script executable
        os.chmod(self.say_script_path, 0o755)
        
    def say(self, to_say: str, first: bool = False, last: bool = False):
        """
        Speaks the string to_say using Choregraphe
        
        Args:
            to_say (str): The string to speak
            first (bool): Not used
            last (bool): If NAO should signal when speaking is done
        """
        print(f"[CHOREGRAPHE NAO SAYS] {to_say}")
        
        # Method 1: Try using Choregraphe's built-in Python script
        try:
            # Create a temporary script that Choregraphe can run
            tmp_script_path = os.path.join(self.behaviors_dir, "temp_say.py")
            with open(tmp_script_path, "w") as f:
                f.write(f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
from naoqi import ALProxy
tts = ALProxy("ALTextToSpeech", "localhost", 9559)
tts.say("{to_say.replace('"', '\\"')}")
''')
            
            # Make it executable
            os.chmod(tmp_script_path, 0o755)
            
            print(f"[CHOREGRAPHE NAO] Running script through Choregraphe")
            print(f"[CHOREGRAPHE NAO] In Choregraphe, use File > Open Script and select:")
            print(f"[CHOREGRAPHE NAO] {tmp_script_path}")
            print(f"[CHOREGRAPHE NAO] Then click Run to make NAO speak")
            
        except Exception as e:
            print(f"[CHOREGRAPHE NAO] Error setting up script: {e}")
        
        # Method 2: Try using a direct command if Choregraphe is connected
        try:
            script_cmd = ["python2.7", self.say_script_path, self.ip, to_say]
            subprocess.run(script_cmd, timeout=5)
        except Exception as e:
            print(f"[CHOREGRAPHE NAO] Error running direct command: {e}")
        
        # Sleep based on text length
        time.sleep(len(to_say.strip()) * self.sleep_len)
        
        if last:
            print("[CHOREGRAPHE NAO] *winks*")


if __name__ == "__main__":
    talker = ChoregrapheTalker(ip="192.168.100.172", language="en")
    talker.say("Hello! This is a test of the Choregraphe talker integration.")