#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Direct NAO Bridge Server - Python 2.7 compatible
This script creates a bridge server that directly communicates with the NAO robot
using the NAOqi SDK. It exposes a simple HTTP API that the main application can use.
"""

import os
import sys
import json
import time
import socket
import threading
# Fix imports for Python 2.7
import BaseHTTPServer
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import SocketServer as socketserver
import urlparse

# Set up logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('direct_nao_bridge')

# Add the NAOqi SDK paths to sys.path - Properly handle macOS Python.framework structure
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# Look for SDK in multiple locations
SDK_LOCATIONS = [
    os.path.join(PROJECT_ROOT, "pynaoqi-sdk"),
    "/app/../pynaoqi",  # Docker location - added missing comma here
    "/Users/yh/Desktop/pynaoqi"  # Desktop location
]

# Find the first SDK location that exists
SDK_DIR = None
for location in SDK_LOCATIONS:
    if os.path.exists(location):
        SDK_DIR = location
        logger.info("Found NAOqi SDK at: {}".format(SDK_DIR))
        break

if SDK_DIR is None:
    logger.error("NAOqi SDK not found in any of the expected locations")
    logger.error("Please download the SDK from https://developer.softbankrobotics.com/nao6/naoqi-developer-guide/sdks/python-sdk")
    logger.error("Expected locations: %s", ", ".join(SDK_LOCATIONS))
    sys.exit(1)

# Check which paths exist and add them to sys.path
potential_paths = [
    os.path.join(SDK_DIR, "lib", "python2.7", "site-packages"),
    os.path.join(SDK_DIR, "lib"),
    os.path.join(SDK_DIR, "Python.framework", "Versions", "2.7", "lib"),
    os.path.join(SDK_DIR, "Python.framework", "Versions", "2.7", "lib", "python2.7", "site-packages"),
    SDK_DIR
]

for path in potential_paths:
    if os.path.exists(path):
        sys.path.insert(0, path)
        logger.info("Added path to sys.path: %s", path)

# Print Python path to help with debugging
logger.info("Python path: %s", sys.path)

# Try to import NAOqi
try:
    # First try the standard import
    from naoqi import ALProxy
    logger.info("NAOqi module imported successfully")
except ImportError as e:
    logger.error("Error importing NAOqi module: %s", e)
    
    # Try to find the naoqi module files manually and add specific locations
    logger.info("Searching for naoqi module in SDK directory...")
    found = False
    for root, dirs, files in os.walk(SDK_DIR):
        if "naoqi.py" in files or "naoqi" in dirs:
            logger.info("Found potential naoqi module at: %s", root)
            if root not in sys.path:
                sys.path.insert(0, root)
                found = True
    
    # If we found naoqi module locations, print updated path
    if found:
        logger.info("Updated Python path: %s", sys.path)
    
    # Try importing specific module components directly
    try:
        import naoqi
        logger.info("Imported naoqi as a package")
        from naoqi import ALProxy
        logger.info("NAOqi module imported successfully on second attempt")
    except ImportError as e:
        logger.error("Still failed to import naoqi. Error: %s", e)
        
        # Last resort: try to import directly from a specific file
        try:
            naoqi_path = os.path.join(SDK_DIR, "lib", "python2.7", "site-packages", "naoqi.py")
            if os.path.exists(naoqi_path):
                import imp
                naoqi = imp.load_source('naoqi', naoqi_path)
                ALProxy = naoqi.ALProxy
                logger.info("NAOqi module loaded directly from file: %s", naoqi_path)
            else:
                logger.error("Could not find naoqi.py file")
                sys.exit(1)
        except Exception as e:
            logger.error("All attempts to import NAOqi failed. Error: %s", e)
            sys.exit(1)

# Configuration
DEFAULT_IP = "192.168.100.172"
DEFAULT_LANGUAGE = "Arabic"
DEFAULT_VOLUME = 80
HOST = "localhost"
PORT = 8080

class NAOController:
    """Controller for interacting with the NAO robot via NAOqi SDK"""
    
    def __init__(self, robot_ip, language, volume):
        """
        Initialize NAO controller
        
        Args:
            robot_ip (str): IP address of the NAO robot
            language (str): Language for the robot to speak
            volume (int): Volume level (0-100)
        """
        self.robot_ip = robot_ip
        self.language = language
        self.volume = volume
        self.tts = None
        self.audio = None
        self.motion = None
        self.connected = False
        
        logger.info("Initializing NAO controller")
        logger.info("Robot IP: %s", robot_ip)
        logger.info("Language: %s", language)
        logger.info("Volume: %s", volume)
        
        # Try to connect to NAO
        self.connect_to_nao()
    
    def connect_to_nao(self):
        """Connect to NAO robot and initialize proxies"""
        try:
            # Check if NAO is reachable
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            result = s.connect_ex((self.robot_ip, 9559))
            s.close()
            
            if result != 0:
                logger.error("NAO robot is not reachable at %s:9559", self.robot_ip)
                return False
            
            # Initialize proxies
            self.tts = ALProxy("ALTextToSpeech", self.robot_ip, 9559)
            self.audio = ALProxy("ALAudioDevice", self.robot_ip, 9559)
            self.motion = ALProxy("ALMotion", self.robot_ip, 9559)
            
            # Set language
            languages = self.tts.getAvailableLanguages()
            logger.info("Available languages: %s", ", ".join(languages))
            
            if self.language in languages:
                self.tts.setLanguage(self.language)
                logger.info("Set language to: %s", self.language)
            else:
                logger.warning("Language %s not available", self.language)
                logger.info("Using robot's current language: %s", self.tts.getLanguage())
            
            # Set volume
            self.audio.setOutputVolume(self.volume)
            logger.info("Set volume to: %s%%", self.volume)
            
            self.connected = True
            logger.info("Successfully connected to NAO robot")
            return True
            
        except Exception as e:
            logger.error("Error connecting to NAO robot: %s", e)
            self.connected = False
            return False
    
    def say(self, text):
        """
        Make the NAO robot say something
        
        Args:
            text (str): Text for the robot to say
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.connected:
            if not self.connect_to_nao():
                logger.error("Not connected to NAO robot")
                return False
        
        try:
            logger.info("NAO says: %s", text)
            
            # Special commands
            if text.lower() == "stand":
                logger.info("NAO is standing up")
                self.motion.wakeUp()
                return True
            elif text.lower() == "sit":
                logger.info("NAO is sitting down")
                self.motion.rest()
                return True
            elif text.lower() == "turnoff":
                logger.info("NAO is turning off eye LEDs")
                leds = ALProxy("ALLeds", self.robot_ip, 9559)
                leds.fade("FaceLeds", 0.0, 1.0)
                return True
            elif text.lower() == "turnon":
                logger.info("NAO is turning on eye LEDs")
                leds = ALProxy("ALLeds", self.robot_ip, 9559)
                leds.fade("FaceLeds", 1.0, 1.0)
                return True
            elif text.lower() == "e":
                logger.info("NAO is nodding")
                # Simple head nod
                self.motion.angleInterpolation(
                    ["HeadPitch"], 
                    [0.0, 0.3, 0.0], 
                    [0.5, 1.0, 1.5], 
                    True
                )
                return True
            
            # Regular speech
            self.tts.say(text)
            return True
            
        except Exception as e:
            logger.error("Error making NAO say something: %s", e)
            self.connected = False
            return False

class NAOBridgeHandler(BaseHTTPRequestHandler):
    """HTTP handler for NAO Bridge requests"""
    
    def log_message(self, format, *args):
        # Override to use our logger
        logger.info("%s - %s", self.address_string(), format % args)
    
    def _set_headers(self, status_code=200):
        """Set response headers"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self._set_headers()
        response = {'status': 'ok'}
        self.wfile.write(json.dumps(response))
    
    def do_POST(self):
        """Handle POST requests to send text to NAO"""
        content_length = int(self.headers.getheader('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            
            if 'text' not in data:
                self._set_headers(400)
                response = {'error': 'No text provided'}
                self.wfile.write(json.dumps(response))
                return
            
            text = data['text']
            
            # Process the request without blocking the response
            def process_nao_request():
                try:
                    nao_controller.say(text)
                except Exception as e:
                    logger.error("Error processing NAO request: %s", e)
            
            # Start a new thread to process the request
            thread = threading.Thread(target=process_nao_request)
            thread.daemon = True
            thread.start()
            
            # Return success immediately
            self._set_headers()
            response = {'success': True}
            self.wfile.write(json.dumps(response))
            
        except ValueError:
            self._set_headers(400)
            response = {'error': 'Invalid JSON'}
            self.wfile.write(json.dumps(response))
        except Exception as e:
            logger.error("Error processing request: %s", e)
            self._set_headers(500)
            response = {'error': str(e)}
            self.wfile.write(json.dumps(response))

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    pass

def run_server(host, port):
    """Run the HTTP server"""
    try:
        server = ThreadedHTTPServer((host, port), NAOBridgeHandler)
        logger.info("Starting Direct NAO Bridge server at http://%s:%s", host, port)
        logger.info("Press Ctrl+C to exit")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server")
        server.socket.close()
    except Exception as e:
        logger.error("Server error: %s", e)

if __name__ == "__main__":
    # Get arguments
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IP
    language = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_LANGUAGE
    volume = int(sys.argv[3]) if len(sys.argv) > 3 else DEFAULT_VOLUME
    
    # Initialize NAO controller
    nao_controller = NAOController(robot_ip, language, volume)
    
    # Start server
    run_server(HOST, PORT)

    # The main issues are related to:
    # 1. NAOqi SDK discovery and loading
    # 2. Docker container environment configuration
    # 3. Script timeout handling
    # Not the HTTP server implementation itself