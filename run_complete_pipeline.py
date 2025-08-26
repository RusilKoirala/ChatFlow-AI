#!/usr/bin/env python3
"""
ChatFlow Setup Script
Complete setup and launch for the ChatFlow conversation platform
"""

import os
import sys
import subprocess
import time
import threading
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.OKBLUE):
    print(f"{color}{message}{Colors.ENDC}")

def print_header(message):
    print_colored(f"\n{'='*50}", Colors.HEADER)
    print_colored(f"  {message}", Colors.HEADER)
    print_colored(f"{'='*50}", Colors.HEADER)

def run_command(command, cwd=None, capture_output=False):
    """Run a command and return success status"""
    try:
        if capture_output:
            result = subprocess.run(command, shell=True, cwd=cwd, 
                                  capture_output=True, text=True, timeout=300)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True, cwd=cwd, timeout=300)
            return result.returncode == 0, "", ""
    except subprocess.TimeoutExpired:
        print_colored("Command timed out!", Colors.FAIL)
        return False, "", "Timeout"
    except Exception as e:
        print_colored(f"Error: {e}", Colors.FAIL)
        return False, "", str(e)

def check_requirements():
    """Check system requirements"""
    print_header("Checking Requirements")
    
    # Check Python
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True)
        version = result.stdout.strip()
        print_colored(f"✓ {version}", Colors.OKGREEN)
    except:
        print_colored("✗ Python not found", Colors.FAIL)
        return False
    
    # Check Node.js
    try:
        result = subprocess.run(["node", "--version"], 
                              capture_output=True, text=True)
        version = result.stdout.strip()
        print_colored(f"✓ Node.js {version}", Colors.OKGREEN)
    except:
        print_colored("✗ Node.js not found - Please install from nodejs.org", Colors.FAIL)
        return False
    
    return True

def setup_ai():
    """Setup conversation model"""
    print_header("Setting up Conversation Model")
    
    if not Path("ai").exists():
        print_colored("✗ AI directory not found", Colors.FAIL)
        return False
    
    # Install dependencies
    print_colored("Installing Python dependencies...", Colors.OKBLUE)
    success, _, error = run_command(f"{sys.executable} -m pip install -r requirements.txt", 
                                   cwd="ai", capture_output=True)
    if not success:
        print_colored(f"✗ Failed: {error}", Colors.FAIL)
        return False
    
    # Check if model exists
    if Path("ai/fine_tuned_model").exists():
        print_colored("✓ Model already trained", Colors.OKGREEN)
        return True
    
    # Train model
    print_colored("Training conversation model...", Colors.OKBLUE)
    success, _, error = run_command(f"{sys.executable} train_model.py", 
                                   cwd="ai", capture_output=True)
    
    if success:
        print_colored("✓ Model trained successfully", Colors.OKGREEN)
        return True
    else:
        print_colored(f"✗ Training failed: {error}", Colors.FAIL)
        return False

def setup_backend():
    """Setup backend server"""
    print_header("Setting up Backend")
    
    if not Path("backend").exists():
        print_colored("✗ Backend directory not found", Colors.FAIL)
        return False
    
    print_colored("Installing dependencies...", Colors.OKBLUE)
    success, _, error = run_command("npm install", cwd="backend", capture_output=True)
    
    if success:
        print_colored("✓ Backend ready", Colors.OKGREEN)
        return True
    else:
        print_colored(f"✗ Failed: {error}", Colors.FAIL)
        return False

def setup_frontend():
    """Setup frontend application"""
    print_header("Setting up Frontend")
    
    if not Path("frontend").exists():
        print_colored("✗ Frontend directory not found", Colors.FAIL)
        return False
    
    print_colored("Installing dependencies...", Colors.OKBLUE)
    success, _, error = run_command("npm install", cwd="frontend", capture_output=True)
    
    if success:
        print_colored("✓ Frontend ready", Colors.OKGREEN)
        return True
    else:
        print_colored(f"✗ Failed: {error}", Colors.FAIL)
        return False

def start_servers():
    """Start the application servers"""
    print_header("Starting ChatFlow")
    
    def start_backend():
        print_colored("Starting backend server...", Colors.OKBLUE)
        subprocess.run("npm start", shell=True, cwd="backend")
    
    def start_frontend():
        time.sleep(2)
        print_colored("Starting frontend...", Colors.OKBLUE)
        subprocess.run("npm run dev", shell=True, cwd="frontend")
    
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    
    backend_thread.start()
    frontend_thread.start()
    
    print_colored("\n" + "="*50, Colors.OKGREEN)
    print_colored("🚀 ChatFlow is running!", Colors.OKGREEN)
    print_colored("="*50, Colors.OKGREEN)
    print_colored("Open: http://localhost:3000", Colors.OKCYAN)
    print_colored("API:  http://localhost:5000", Colors.OKCYAN)
    print_colored("="*50, Colors.OKGREEN)
    print_colored("\nPress Ctrl+C to stop", Colors.WARNING)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print_colored("\nShutting down...", Colors.WARNING)
        sys.exit(0)

def main():
    """Main setup function"""
    print_colored("""
    ╔════════════════════════════════════════════╗
    ║                                            ║
    ║           💬 ChatFlow Setup 💬            ║
    ║                                            ║
    ║     Intelligent Conversation Platform      ║
    ║                                            ║
    ╚════════════════════════════════════════════╝
    """, Colors.HEADER)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup components
    if not setup_ai():
        sys.exit(1)
    
    if not setup_backend():
        sys.exit(1)
        
    if not setup_frontend():
        sys.exit(1)
    
    # Success message
    print_colored("\n" + "="*50, Colors.OKGREEN)
    print_colored("✅ Setup completed successfully!", Colors.OKGREEN)
    print_colored("="*50, Colors.OKGREEN)
    
    # Ask to start
    start_now = input(f"{Colors.OKBLUE}Start ChatFlow now? (y/n): {Colors.ENDC}").strip().lower()
    
    if start_now in ['y', 'yes', '']:
        start_servers()
    else:
        print_colored("\nTo start later:", Colors.OKCYAN)
        print_colored("  npm run dev", Colors.OKCYAN)
        print_colored("  Then open http://localhost:3000", Colors.OKCYAN)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\nSetup cancelled", Colors.WARNING)
        sys.exit(1)
    except Exception as e:
        print_colored(f"Error: {e}", Colors.FAIL)
        sys.exit(1)