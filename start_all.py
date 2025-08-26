#!/usr/bin/env python3
"""
Quick start script for ChatFlow
Starts both backend and frontend servers
"""

import subprocess
import threading
import time
import sys

def start_backend():
    """Start the backend server"""
    print("🔧 Starting backend server...")
    subprocess.run("npm start", shell=True, cwd="backend")

def start_frontend():
    """Start the frontend development server"""
    time.sleep(2)  # Wait for backend to start
    print("🎨 Starting frontend...")
    subprocess.run("npm run dev", shell=True, cwd="frontend")

def main():
    print("""
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║           💬 Starting ChatFlow 💬          ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    """)
    
    # Start servers in separate threads
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    
    backend_thread.start()
    frontend_thread.start()
    
    print("\n" + "="*50)
    print("🚀 ChatFlow is starting...")
    print("="*50)
    print("Frontend: http://localhost:3000")
    print("Backend:  http://localhost:5000")
    print("="*50)
    print("\nPress Ctrl+C to stop servers")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down servers...")
        sys.exit(0)

if __name__ == "__main__":
    main()