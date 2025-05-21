#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
"""
Simple NAOqi import test
"""

import os
import sys

# Print paths
print("Current directories in sys.path:")
for p in sys.path:
    print("- {}".format(p))

# Add the NAOqi SDK paths to sys.path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
SDK_DIR = os.path.join(PROJECT_ROOT, "pynaoqi-sdk")

print("\nAdding SDK paths...")
# Add standard paths
sdk_paths = [
    SDK_DIR, 
    os.path.join(SDK_DIR, "lib"),
]

# Add paths and check if they exist
for path in sdk_paths:
    if os.path.exists(path):
        sys.path.insert(0, path)
        print("Added: {}".format(path))
    else:
        print("Path doesn't exist: {}".format(path))

# List contents of SDK_DIR/lib if it exists
lib_path = os.path.join(SDK_DIR, "lib")
if os.path.exists(lib_path):
    print("\nContents of SDK lib directory:")
    try:
        for item in os.listdir(lib_path):
            print("- {}".format(item))
    except Exception as e:
        print("Error listing directory: {}".format(e))

# Try to import naoqi
print("\nAttempting to import naoqi...")
try:
    from naoqi import ALProxy
    print("SUCCESS: naoqi module imported!")
except ImportError as e:
    print("FAILED: {}".format(e))

# Try to import specific naoqi modules
print("\nTrying to locate naoqi module on disk...")
for root, dirs, files in os.walk(SDK_DIR):
    for name in dirs:
        if name == "naoqi":
            print("Found naoqi directory: {}".format(os.path.join(root, name)))
    for name in files:
        if name.startswith("naoqi") and (name.endswith(".py") or name.endswith(".so")):
            print("Found naoqi file: {}".format(os.path.join(root, name)))