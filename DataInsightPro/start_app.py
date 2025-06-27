#!/usr/bin/env python3
"""
Startup script for the SQL Data Analysis Tool
Ensures proper port binding and startup detection
"""

import subprocess
import time
import socket
import sys
import os

def check_port(port, timeout=30):
    """Check if port is available and listening"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False

def main():
    """Main startup function"""
    port = 5000
    
    print(f"Starting SQL Data Analysis Tool on port {port}...")
    
    # Start Streamlit in the background
    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true"
    ]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for port to be available
        if check_port(port):
            print(f"✓ Server is running on port {port}")
            print(f"  URL: http://0.0.0.0:{port}")
            # Keep the process running
            process.wait()
        else:
            print(f"✗ Failed to start server on port {port}")
            process.terminate()
            sys.exit(1)
            
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()