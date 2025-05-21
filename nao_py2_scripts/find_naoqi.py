#!/usr/bin/env python2.7
"""
NAOqi SDK Finder - Diagnostic script to locate NAOqi SDK modules
This script helps to identify where the NAOqi SDK is installed and which paths should be used.
"""

import os
import sys
import platform

print("=" * 50)
print("NAOqi SDK Finder - Diagnostic Tool")
print("=" * 50)
print("Python version: {}".format(sys.version))
print("Platform: {}".format(platform.platform()))
print("Architecture: {}".format(platform.machine()))

# Current directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sdk_dir = os.path.join(project_root, "pynaoqi-sdk")

print("\nLooking for NAOqi SDK in: {}".format(sdk_dir))
print("-" * 50)

if os.path.exists(sdk_dir):
    print("[✓] SDK directory found")
    
    # List main directories in SDK
    print("\nMain directories in SDK:")
    for item in os.listdir(sdk_dir):
        item_path = os.path.join(sdk_dir, item)
        if os.path.isdir(item_path):
            print("- {} (directory)".format(item))
        else:
            print("- {} (file)".format(item))
    
    # Look for Python.framework structure (macOS specific)
    py_framework = os.path.join(sdk_dir, "Python.framework")
    if os.path.exists(py_framework):
        print("\n[✓] Python.framework found")
        versions_dir = os.path.join(py_framework, "Versions")
        if os.path.exists(versions_dir):
            print("Versions available:")
            for version in os.listdir(versions_dir):
                if os.path.isdir(os.path.join(versions_dir, version)):
                    print("- {}".format(version))
    
    # Look for lib directory structure
    lib_dir = os.path.join(sdk_dir, "lib")
    if os.path.exists(lib_dir):
        print("\n[✓] lib directory found")
        print("Contents:")
        for item in os.listdir(lib_dir):
            print("- {}".format(item))
    
    # Try to locate naoqi module
    print("\nSearching for naoqi module...")
    naoqi_locations = []
    for root, dirs, files in os.walk(sdk_dir):
        if "naoqi.py" in files or "naoqi" in dirs:
            rel_path = os.path.relpath(root, sdk_dir)
            naoqi_locations.append(rel_path)
    
    if naoqi_locations:
        print("[✓] Potential naoqi module locations:")
        for loc in naoqi_locations:
            print("- {}".format(os.path.join(sdk_dir, loc)))
    else:
        print("[✗] Could not find naoqi module")
    
    # Generate import paths to add to sys.path
    print("\nRecommended import paths to add to sys.path:")
    recommended_paths = [
        sdk_dir,
        os.path.join(sdk_dir, "lib"),
        os.path.join(sdk_dir, "lib", "python2.7", "site-packages") if os.path.exists(os.path.join(sdk_dir, "lib", "python2.7", "site-packages")) else None,
        os.path.join(sdk_dir, "Python.framework", "Versions", "2.7", "lib") if os.path.exists(os.path.join(sdk_dir, "Python.framework", "Versions", "2.7", "lib")) else None,
        os.path.join(sdk_dir, "Python.framework", "Versions", "2.7", "lib", "python2.7", "site-packages") if os.path.exists(os.path.join(sdk_dir, "Python.framework", "Versions", "2.7", "lib", "python2.7", "site-packages")) else None
    ]
    
    for path in recommended_paths:
        if path and os.path.exists(path):
            print("sys.path.insert(0, '{}')".format(path))
    
    # Try to import naoqi
    print("\nTrying to import naoqi module...")
    for path in recommended_paths:
        if path and os.path.exists(path):
            sys.path.insert(0, path)
    
    try:
        import naoqi
        print("[✓] Successfully imported naoqi module")
        print("naoqi module location: {}".format(naoqi.__file__))
        print("naoqi version: {}".format(getattr(naoqi, "__version__", "Unknown")))
    except ImportError as e:
        print("[✗] Failed to import naoqi module: {}".format(e))
        print("Current sys.path:")
        for p in sys.path:
            print("- {}".format(p))
else:
    print("[✗] SDK directory not found at: {}".format(sdk_dir))

print("\n" + "=" * 50)