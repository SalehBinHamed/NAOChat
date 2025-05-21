#!/bin/bash
# Start the direct NAO bridge server using Python 2.7

# Default values
IP=${1:-"192.168.100.172"}
LANGUAGE=${2:-"Arabic"}
VOLUME=${3:-"80"}

# Path to this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BRIDGE_SCRIPT="$SCRIPT_DIR/direct_nao_bridge.py"

# Check if Python 2.7 is available
PYTHON27_PATH=$(which python2.7)
if [ -z "$PYTHON27_PATH" ]; then
    echo "Python 2.7 not found. Please install Python 2.7."
    exit 1
fi

# Make the script executable if it's not already
if [ ! -x "$BRIDGE_SCRIPT" ]; then
    chmod +x "$BRIDGE_SCRIPT"
fi

echo "Starting Direct NAO Bridge Server..."
echo "IP: $IP"
echo "Language: $LANGUAGE"
echo "Volume: $VOLUME"

# Run the bridge script with Python 2.7
exec "$PYTHON27_PATH" "$BRIDGE_SCRIPT" "$IP" "$LANGUAGE" "$VOLUME"