#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This script uses the NAO's HTTP API instead of the NAOqi SDK
# This approach avoids the SSL compatibility issues

import sys
import requests
import json
import time
import urllib

def send_text_to_nao(robot_ip, text, language="English", volume=80):
    """
    Send text to NAO robot using its HTTP API
    """
    print("Sending to NAO at {}: {}".format(robot_ip, text))
    
    # First check if the robot is reachable
    try:
        # Check if robot is reachable
        test_url = "http://{}".format(robot_ip)
        response = requests.get(test_url, timeout=5)
        print("NAO robot is reachable!")
    except requests.exceptions.RequestException as e:
        print("Error connecting to NAO robot: {}".format(e))
        print("Make sure your NAO is powered on and connected to the network.")
        return False
    
    # Try different HTTP API approaches
    
    # Method 1: Using the simple ALTextToSpeech API
    try:
        url = "http://{}/command.json".format(robot_ip)
        
        # URL encode the text
        encoded_text = urllib.parse.quote(text)
        
        # Build the data payload
        data = {
            "component": "ALTextToSpeech",
            "method": "say",
            "parameters": {
                "value": text
            }
        }
        
        # Send the request
        response = requests.post(url, json=data, timeout=5)
        
        if response.status_code == 200:
            print("Method 1: Message successfully sent to NAO!")
            return True
        else:
            print("Method 1 failed. Status code: {}".format(response.status_code))
            print("Response: {}".format(response.text))
    except Exception as e:
        print("Method 1 failed with error: {}".format(e))
    
    # Method 2: Using the legacy API
    try:
        url = "http://{}/apps/dialog/say?text={}".format(robot_ip, urllib.parse.quote(text))
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            print("Method 2: Message successfully sent to NAO!")
            return True
        else:
            print("Method 2 failed. Status code: {}".format(response.status_code))
    except Exception as e:
        print("Method 2 failed with error: {}".format(e))
    
    # Method 3: Using the RAW API call
    try:
        url = "http://{}:80/".format(robot_ip)
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = "say={}".format(urllib.parse.quote(text))
        response = requests.post(url, headers=headers, data=data, timeout=5)
        
        if response.status_code == 200:
            print("Method 3: Message successfully sent to NAO!")
            return True
        else:
            print("Method 3 failed. Status code: {}".format(response.status_code))
    except Exception as e:
        print("Method 3 failed with error: {}".format(e))
    
    print("All methods failed to send text to NAO.")
    return False

def main():
    """Main function to handle command-line arguments"""
    # Get robot IP from command line or use default
    robot_ip = sys.argv[1] if len(sys.argv) > 1 else "192.168.100.172"
    
    # Get text from command line or use default
    text = sys.argv[2] if len(sys.argv) > 2 else "Hello, I am NAO. Can you hear me now?"
    
    # Send the text to NAO
    return 0 if send_text_to_nao(robot_ip, text) else 1

if __name__ == "__main__":
    sys.exit(main())