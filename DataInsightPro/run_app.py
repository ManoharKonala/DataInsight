#!/usr/bin/env python3
"""
Robust startup script for SQL Data Analysis Tool
"""
import subprocess
import sys
import time
import socket
import os

def check_port_available(port):
    """Check if port is available for binding"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.close()
        return True
    except OSError:
        return False

def check_port_listening(port, timeout=30):
    """Check if port is listening for connections"""
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
    port = 5000
    
    # Check if port is available
    if not check_port_available(port):
        print(f"Port {port} is already in use. Cleaning up...")
        os.system(f"pkill -f streamlit")
        time.sleep(2)
        
        if not check_port_available(port):
            print(f"Cannot free port {port}")
            sys.exit(1)
    
    print(f"Starting SQL Data Analysis Tool on port {port}...")
    
    # Start Streamlit
    cmd = [
        "streamlit", "run", "app.py",
        "--server.port", str(port),
        "--server.address", "0.0.0.0",
        "--server.headless", "true",
        "--browser.gatherUsageStats", "false"
    ]
    
    try:
        process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitor startup
        startup_timeout = 30
        start_time = time.time()
        
        while time.time() - start_time < startup_timeout:
            # Check if process is still running
            if process.poll() is not None:
                output, _ = process.communicate()
                print(f"Process exited early: {output}")
                sys.exit(1)
            
            # Check if port is listening
            if check_port_listening(port, 1):
                print(f"Server is ready on port {port}")
                print(f"URL: http://0.0.0.0:{port}")
                break
            
            time.sleep(1)
        else:
            print("Startup timeout reached")
            process.terminate()
            sys.exit(1)
        
        # Keep process running
        try:
            process.wait()
        except KeyboardInterrupt:
            print("Shutting down...")
            process.terminate()
            
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()