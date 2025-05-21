#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Direct Terminal-to-ChatGPT-to-NAO Integration Script
This script takes input from the terminal, sends it to ChatGPT,
and creates a script for Choregraphe to make NAO speak the response.
"""

import os
import sys
import time
from pathlib import Path

# Add the src directory to the path to import Chatter
script_dir = os.path.dirname(os.path.abspath(__file__))
project_dir = os.path.dirname(script_dir)
src_dir = os.path.join(project_dir, "src")
sys.path.append(src_dir)

try:
    from Chatter import Chatter
except ImportError:
    print("Error importing Chatter. Make sure the environment is set up correctly.")
    sys.exit(1)

def create_choregraphe_script(text):
    """Create a Python script that can be run in Choregraphe to make NAO speak"""
    script_path = os.path.join(script_dir, "nao_response.py")
    with open(script_path, 'w') as f:
        f.write(f'''#!/usr/bin/env python
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
    response_text = """{text.replace('"', '\\"')}"""
    
    # Make NAO speak the response
    print("NAO is saying: " + response_text)
    tts.say(response_text)
    
    print("Speech completed successfully!")
except Exception as e:
    print("Error:", e)
''')
    print(f"\n✓ NAO speech script created at: {script_path}")
    print("→ Open this script in Choregraphe and run it to make NAO speak")
    return script_path

def main():
    print("\n====== NAO ChatGPT Terminal Interface ======")
    print("Type your message to send to ChatGPT.")
    print("ChatGPT's response will be prepared for NAO to speak.")
    print("Type 'exit' or 'quit' to end the session.")
    print("===========================================\n")
    
    # Initialize the chatbot with a simple prompt for NAO
    nao_prompt = "You are NAO, a friendly humanoid robot assistant. Keep your responses concise, under 50 words, and suitable for a robot to speak naturally."
    chatbot = Chatter(nao_prompt, stream=False)
    
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting...")
                break
                
            if not user_input:
                continue
                
            print("\nSending to ChatGPT...")
            # Get response from ChatGPT
            response = chatbot(user_input)
            
            print(f"\nChatGPT Response:\n{response}")
            
            # Create the script for Choregraphe to make NAO speak
            script_path = create_choregraphe_script(response)
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    main()