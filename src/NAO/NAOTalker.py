import sys
from os import path
# Append to path to find the "Talker" class in the parent dictionary
sys.path.append(path.dirname(path.dirname(path.realpath(__file__))))
from Talker import Talker
import subprocess as sp
import time
import iso639
import requests
import json

# Helper function to convert language code to language name
def get_language_name(language_code):
    try:
        # Try using iso639.languages.get method first (for iso639 package)
        return iso639.languages.get(part1=language_code).name
    except (AttributeError, KeyError):
        # Fallback: Map common language codes manually
        language_map = {
            'en': 'English',
            'ar': 'Arabic',
            'fr': 'French',
            'es': 'Spanish',
            'de': 'German',
            'it': 'Italian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'zh': 'Chinese',
            'sv': 'Swedish'
        }
        return language_map.get(language_code, 'English')  # Default to English if not found

# Class for connecting to physical NAO robot via the bridge server
class BridgeNAOTalker(Talker):
    def __init__(self, ip: str, language: str = "en", sleep_len: float = 0.03, stand=False, volume: int = 100):
        super().__init__(language = language)
        self.ip = ip
        self.sleep_len = sleep_len
        self.language = get_language_name(language)
        self.volume = volume
        self.standing = stand
        self.bridge_url = "http://localhost:8080"
        
        print(f"[BRIDGE NAO] Setting up connection to NAO at IP: {ip}")
        print(f"[BRIDGE NAO] Language: {self.language}")
        print(f"[BRIDGE NAO] Volume: {volume}")

        # Try to connect to the bridge server
        connected = False
        try:
            response = requests.options(self.bridge_url, timeout=2)
            if response.status_code == 200:
                connected = True
                print("[BRIDGE NAO] Successfully connected to bridge server")
        except Exception as e:
            print(f"[BRIDGE NAO] Could not connect to bridge server: {str(e)}")
            
        if not connected:
            print("[BRIDGE NAO] Please start the bridge server with:")
            print(f"python /Users/yh/Desktop/NAOChat/nao_py2_scripts/nao_bridge.py {ip} {self.language} {volume}")
            print("[BRIDGE NAO] Falling back to mock NAO")
            
            # Instead of raising an error, we'll switch to mock mode
            self.mock_mode = True
            print("[BRIDGE NAO] Operating in mock mode - commands will be displayed but not sent to robot")
        else:
            self.mock_mode = False
            
            # Customize the connection message based on language
            if language == "ar":
                connection_message = "تم الاتصال بنجاح"  # "Connected successfully" in Arabic
            elif language == "en":
                connection_message = "Connected successfully"
            else:
                connection_message = "Connected successfully"
                
            # Send the connection message to the physical robot
            print(f"[BRIDGE NAO] Sending connection confirmation to NAO: {connection_message}")
            self.send_to_nao(connection_message)
            time.sleep(2)  # Give time for the robot to speak
            
            if stand:
                self.send_to_nao("stand")

    def __del__(self):
        if hasattr(self, 'standing') and self.standing and not getattr(self, 'mock_mode', True):
            self.send_to_nao("sit")

    def send_to_nao(self, to_say):
        if getattr(self, 'mock_mode', True):
            print(f"[MOCK NAO] {to_say}")
            return True
            
        try:
            data = {"text": to_say}
            response = requests.post(self.bridge_url, json=data, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"[BRIDGE NAO] Error sending to NAO: {e}")
            return False

    def say(self, to_say: str, first: bool = False, last: bool = False):
        """
        Speaks the string to_say

        Args:
            to_say (str): The string to speak
            first (bool): Not used
            last (bool): If NAO should signal when speaking is done via winking
        """
        if getattr(self, 'mock_mode', True):
            print(f"[MOCK NAO SAYS] {to_say}")
        else:
            print(f"[BRIDGE NAO SAYS] {to_say}")
            
        self.send_to_nao(to_say)
        time.sleep(len(to_say.strip())*self.sleep_len)
        if last:
            self.send_to_nao('turnoff')
            self.send_to_nao('turnon')
            if self.standing:
                self.send_to_nao('e')

# Add a mock version for testing without NAO hardware
class MockNAOTalker(Talker):
    def __init__(self, ip: str, language: str = "en", sleep_len: float = 0.03, stand=False, volume: int = 100):
        super().__init__(language = language)
        self.ip = ip
        self.sleep_len = sleep_len
        self.language = get_language_name(language)
        self.volume = volume
        self.standing = stand
        print(f"[MOCK NAO] Connected to NAO at IP: {ip}")
        print(f"[MOCK NAO] Language: {self.language}")
        print(f"[MOCK NAO] Volume: {volume}")
        if stand:
            print(f"[MOCK NAO] Standing up...")

    def __del__(self):
        if hasattr(self, 'standing') and self.standing:
            print(f"[MOCK NAO] Sitting down...")

    def nao_say(self, to_say):
        print(f"[MOCK NAO] {to_say}")

    def say(self, to_say: str, first: bool = False, last: bool = False):
        """
        Speaks the string to_say

        Args:
            to_say (str): The string to speak
            first (bool): Not used
            last (bool): If NAO should signal when speaking is done via winking
        """
        print(f"[MOCK NAO SAYS] {to_say}")
        time.sleep(len(to_say.strip())*self.sleep_len)
        if last:
            print("[MOCK NAO] *winks*")

# Try to use the BridgeNAOTalker first, then fall back to MockNAOTalker
try:
    # Try to import requests for the bridge
    import requests
    
    # Define the NAOTalker as BridgeNAOTalker
    NAOTalker = BridgeNAOTalker
    
except (ImportError, ConnectionError):
    # If bridge requirements are not met, use the mock version
    print("Bridge server not available. Using MockNAOTalker instead.")
    NAOTalker = MockNAOTalker

if __name__ == "__main__":
    from Chatter import Chatter
    from Listener import Listener
    name = "Pepper"
    swe_intro = f"Du är den mänskliga roboten {name}. En NAO-modellrobot byggd av Softbank och programmerad av FIA Robotics. Din uppgift är att hålla en intressant konversation med en grupp människor. Du får max svara med två meningar."
    eng_intro = f"You are the humanoid robot {name}. A NAO model robot built by Softbank and programmed by FIA Robotics. Your task is to hold an interesting conversation with a group of humans. You can at most answer with two sentences"
    chatter = Chatter(eng_intro, stream=True,chat_horison=5,filt_horizon=-1)
    listener = Listener(language="en",use_whisper=False) # Change to 'sv' for Swedish
    talker = NAOTalker(ip="192.168.100.172",language="ar")
    while(True):
        print(f"Listening")
        heard = listener()
        print(f"Heard: {heard}")
        if heard != "":
            response = chatter(heard)
            talker(response)
