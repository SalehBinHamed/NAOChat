#!/bin/bash
# Script to find NAO robots on the local network

echo "==== NAO Robot Network Scanner ===="

# Check for required dependencies
check_dependencies() {
  local missing_deps=()
  
  # Check for nmap
  if ! command -v nmap &>/dev/null; then
    missing_deps+=("nmap")
  fi
  
  # Check for nc (netcat)
  if ! command -v nc &>/dev/null; then
    missing_deps+=("netcat")
  fi
  
  # If there are missing dependencies, suggest installation
  if [ ${#missing_deps[@]} -gt 0 ]; then
    echo "Missing required dependencies: ${missing_deps[*]}"
    echo "Please install them using Homebrew:"
    echo "brew install ${missing_deps[*]}"
    exit 1
  fi
}

# Run dependency check
check_dependencies

echo "Scanning network for NAO robots..."

# Determine network interface and IP
INTERFACE=$(route -n get default | grep interface | awk '{print $2}')
if [ -z "$INTERFACE" ]; then
  echo "Error: Couldn't determine network interface."
  echo "Trying alternative method..."
  INTERFACE=$(netstat -rn | grep default | head -1 | awk '{print $NF}')
fi

if [ -z "$INTERFACE" ]; then
  echo "Error: Still couldn't determine network interface."
  echo "Please check your network connection."
  exit 1
fi

MY_IP=$(ifconfig $INTERFACE | grep "inet " | awk '{print $2}')
if [ -z "$MY_IP" ]; then
  echo "Error: Couldn't determine your IP address."
  exit 1
fi

SUBNET=$(echo $MY_IP | cut -d. -f1-3)

echo "Your IP address: $MY_IP"
echo "Network interface: $INTERFACE"
echo "Scanning subnet: $SUBNET.0/24"
echo "This may take a minute..."

# Function to check if a host is likely a NAO robot
check_nao() {
  local ip=$1
  # Check if port 9559 (NAOqi) is open
  if nc -z -w 1 -G 1 $ip 9559 &>/dev/null; then
    echo "Found potential NAO robot at $ip (NAOqi port 9559 is open)"
    echo "$ip" >> /tmp/nao_robots.txt
    return 0
  fi
  return 1
}

# Clear previous results
rm -f /tmp/nao_robots.txt

# Ping scan to find live hosts (faster than full port scan)
echo "Running network scan with nmap (this may take 30-60 seconds)..."
nmap -sn $SUBNET.0/24 -oG - | grep "Up" | awk '{print $2}' > /tmp/live_hosts.txt

# Check if any hosts were found
if [ ! -s /tmp/live_hosts.txt ]; then
  echo "No hosts found on the network. This is unusual."
  echo "Trying alternative scan method..."
  
  # Alternative: Simple ping sweep
  for i in $(seq 1 254); do
    (ping -c 1 -W 1 $SUBNET.$i &>/dev/null && echo "$SUBNET.$i" >> /tmp/live_hosts.txt) &
    # Run 10 pings in parallel to speed things up
    [ $((i % 10)) -eq 0 ] && wait
  done
  wait
fi

# Check if we found any hosts with alternative method
if [ ! -s /tmp/live_hosts.txt ]; then
  echo "Still no hosts found. Please check your network connection."
  exit 1
fi

echo "Found $(wc -l < /tmp/live_hosts.txt) active hosts on your network."
echo "Checking for NAO robots on discovered hosts..."

# Check each live host for NAO robot signatures
while read ip; do
  check_nao $ip &
done < /tmp/live_hosts.txt

# Wait for all background processes to complete
wait

# Also check the specific IP address you've been trying previously
if ! grep -q "192.168.100.172" /tmp/live_hosts.txt; then
  echo "Checking the specific NAO IP (192.168.100.172) that you've been using..."
  check_nao 192.168.100.172
  wait
fi

# Display results
echo ""
echo "==== Scan Complete ===="
if [ -f /tmp/nao_robots.txt ] && [ -s /tmp/nao_robots.txt ]; then
  echo "Found $(wc -l < /tmp/nao_robots.txt) potential NAO robot(s):"
  cat /tmp/nao_robots.txt
  
  # Test connection to the first found robot
  FIRST_NAO=$(head -1 /tmp/nao_robots.txt)
  echo ""
  echo "Testing connection to NAO at $FIRST_NAO..."
  if ping -c 2 $FIRST_NAO &>/dev/null; then
    echo "NAO robot at $FIRST_NAO is reachable via ping."
    echo "You can use this IP with the nao_connect.sh script."
    
    # Try to get some info from the NAO
    echo "Checking if NAOqi API port is accessible..."
    if nc -z -w 1 $FIRST_NAO 9559; then
      echo "NAOqi API port (9559) is open! The robot is ready to accept commands."
    else
      echo "Warning: NAOqi API port (9559) is not responding even though we detected it earlier."
      echo "The robot may be in a transitional state. Try again in a moment."
    fi
  else
    echo "Warning: NAO robot at $FIRST_NAO is not responding to ping."
    echo "However, it was detected on port 9559, so it might still be usable."
  fi
else
  echo "No NAO robots found on the network."
  echo "Make sure your NAO robot is:"
  echo "1. Powered on (check for chest button light)"
  echo "2. Connected to the same network as your computer"
  echo "3. Fully booted (boot process takes about 1-2 minutes)"
  echo ""
  echo "You could also try connecting directly to the NAO by its IP address:"
  echo "./nao_connect.sh 192.168.100.172"
fi

# Clean up
rm -f /tmp/live_hosts.txt /tmp/nao_robots.txt