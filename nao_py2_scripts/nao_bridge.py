#!/usr/bin/env python3
"""
NAO Bridge - Connects NAOChat to physical NAO robot
This script creates a simple server that listens for messages from the main NAOChat application
and forwards them to the NAO robot via the Docker container.
"""

import subprocess
import sys
import os
import threading
import tempfile
import time
import json
import logging
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger('nao_bridge')

# Configuration
DEFAULT_IP = "192.168.100.172"
DEFAULT_LANGUAGE = "Arabic" 
DEFAULT_VOLUME = "100"
HOST = "localhost"
PORT = 8080
DOCKER_TIMEOUT = 10  # Seconds to wait for Docker command

class NAOBridge:
    def __init__(self, robot_ip, language, volume):
        self.robot_ip = robot_ip
        self.language = language
        self.volume = volume
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.docker_script = os.path.join(self.script_dir, "run_docker_nao.sh")
        
        # Ensure the Docker script is executable
        if not os.access(self.docker_script, os.X_OK):
            os.chmod(self.docker_script, 0o755)
            
        logger.info(f"NAO Bridge initialized for robot at {robot_ip}")
        logger.info(f"Language: {language}")
        logger.info(f"Volume: {volume}")
        
        # Test Docker availability
        try:
            result = subprocess.run(
                ["docker", "--version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"Docker is available: {result.stdout.strip()}")
            else:
                logger.error(f"Docker is not working properly: {result.stderr.strip()}")
        except Exception as e:
            logger.error(f"Error checking Docker: {e}")
    
    def send_to_nao(self, text):
        """Send text to the NAO robot using the Docker container"""
        if not text.strip():
            return False
            
        logger.info(f"Sending to NAO: {text}")
        
        try:
            # Instead of using stdin/stdout pipes which can cause broken pipe errors,
            # pass the text directly to the script as a command line argument
            
            # Create a temporary file with the message
            temp_file = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
                    f.write(text)
                    temp_file = f.name
                
                # Run the Docker script with the text as an argument
                def run_docker():
                    try:
                        # Use subprocess.run instead of Popen for simplified process management
                        result = subprocess.run(
                            [self.docker_script, self.robot_ip, self.language, self.volume, temp_file],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            timeout=DOCKER_TIMEOUT
                        )
                        
                        if result.returncode != 0:
                            logger.error(f"Docker process error (exit code {result.returncode}): {result.stderr}")
                        else:
                            logger.debug("Docker process completed successfully")
                            
                    except subprocess.TimeoutExpired:
                        logger.warning("Docker process timed out")
                    except Exception as e:
                        logger.error(f"Error in Docker thread: {e}")
                
                # Start the Docker process in a separate thread
                thread = threading.Thread(target=run_docker)
                thread.daemon = True
                thread.start()
                
                # Return immediately - don't wait for the Docker process
                return True
                
            finally:
                # Schedule temp file deletion (don't delete immediately as Docker might still need it)
                if temp_file:
                    def cleanup_temp_file():
                        try:
                            time.sleep(5)  # Give Docker time to read the file
                            if os.path.exists(temp_file):
                                os.remove(temp_file)
                        except Exception as e:
                            logger.error(f"Error cleaning up temp file: {e}")
                    
                    cleanup_thread = threading.Thread(target=cleanup_temp_file)
                    cleanup_thread.daemon = True
                    cleanup_thread.start()
                
        except Exception as e:
            logger.error(f"Error sending to NAO: {e}")
            return False

class NAOBridgeHandler(BaseHTTPRequestHandler):
    """HTTP handler for NAO Bridge requests"""
    
    def log_message(self, format, *args):
        # Override to use our logger
        logger.info(f"{self.address_string()} - {format % args}")
    
    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
    def do_POST(self):
        """Handle POST requests to send text to the NAO robot"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            
            if 'text' not in data:
                self._set_headers(400)
                self.wfile.write(json.dumps({'error': 'No text provided'}).encode('utf-8'))
                return
                
            # Process the request without waiting for completion
            nao_bridge.send_to_nao(data['text'])
            
            # Return success immediately
            self._set_headers(200)
            response = {'success': True}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        except json.JSONDecodeError:
            self._set_headers(400)
            self.wfile.write(json.dumps({'error': 'Invalid JSON'}).encode('utf-8'))
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            self._set_headers(500)
            self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
    
    def do_OPTIONS(self):
        """Handle OPTIONS requests for CORS"""
        self._set_headers()
        self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))

def run_server(host, port):
    """Run the HTTP server"""
    try:
        server = HTTPServer((host, port), NAOBridgeHandler)
        logger.info(f"Starting NAO Bridge server at http://{host}:{port}")
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server")
        server.socket.close()
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    # Get arguments
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_IP
    language = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_LANGUAGE
    volume = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_VOLUME
    
    # Initialize NAO Bridge
    global nao_bridge
    nao_bridge = NAOBridge(robot_ip, language, volume)
    
    # Start server
    run_server(HOST, PORT)