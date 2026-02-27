#!/usr/bin/env python3
"""
DeepSeek-V3 Fixed Installer for Windows 11 Pro
by nu11secur1ty
Run: python install_deepseek_final_v2.py
"""

import os
import sys
import subprocess
import time
import ctypes
import urllib.request
import winreg
from pathlib import Path

# Configuration
CONFIG = {
    "model_size": "14b",     # Options: "1.5b", "7b", "8b", "14b", "32b", "70b"
    "port": 3000,
}

# Windows-compatible colors
class Colors:
    def __init__(self):
        self.enabled = self._supports_color()
    
    def _supports_color(self):
        if os.environ.get('WT_SESSION'): return True
        if os.environ.get('TERM_PROGRAM') == 'vscode': return True
        if os.environ.get('ConEmuANSI') == 'ON': return True
        return False
    
    def green(self, text): return f"\033[92m{text}\033[0m" if self.enabled else text
    def yellow(self, text): return f"\033[93m{text}\033[0m" if self.enabled else text
    def red(self, text): return f"\033[91m{text}\033[0m" if self.enabled else text
    def blue(self, text): return f"\033[94m{text}\033[0m" if self.enabled else text
    def cyan(self, text): return f"\033[96m{text}\033[0m" if self.enabled else text

colors = Colors()

def print_step(message): print(colors.blue(f"➜ {message}"))
def print_success(message): print(colors.green(f"✓ {message}"))
def print_warning(message): print(colors.yellow(f"⚠ {message}"))
def print_error(message): print(colors.red(f"✗ {message}"))
def print_header(message): 
    print(colors.cyan("=" * 60))
    print(colors.cyan(message.center(60)))
    print(colors.cyan("=" * 60))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_powershell(command):
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0, result.stdout, result.stderr
    except:
        return False, "", ""

def download_with_progress(url, filename):
    """Download with progress bar"""
    try:
        print_step(f"Downloading {filename}...")
        
        # Check if file exists and get size
        downloaded = 0
        if os.path.exists(filename):
            downloaded = os.path.getsize(filename)
            print(f"  Resuming from {downloaded/(1024*1024):.1f}MB")
        
        # Set up request with range if partial
        req = urllib.request.Request(url)
        if downloaded > 0:
            req.add_header('Range', f'bytes={downloaded}-')
        
        with urllib.request.urlopen(req) as response:
            total = int(response.headers.get('content-length', 0)) + downloaded
            
            mode = 'ab' if downloaded > 0 else 'wb'
            with open(filename, mode) as f:
                start_time = time.time()
                block_size = 8192
                downloaded_current = downloaded
                
                while True:
                    buffer = response.read(block_size)
                    if not buffer:
                        break
                    
                    f.write(buffer)
                    downloaded_current += len(buffer)
                    
                    if total > 0:
                        percent = (downloaded_current / total) * 100
                        elapsed = time.time() - start_time
                        speed = downloaded_current / (1024*1024) / elapsed if elapsed > 0 else 0
                        
                        print(f"\r  Progress: {percent:.1f}% ({downloaded_current/(1024*1024):.1f}/{total/(1024*1024):.1f}MB) {speed:.1f}MB/s", end="")
        
        print(f"\n{colors.green('✓ Download complete!')}")
        return True
        
    except KeyboardInterrupt:
        print(f"\n{colors.yellow('⚠ Download paused. Run again to resume.')}")
        return False
    except Exception as e:
        print_error(f"Download failed: {e}")
        return False

def install_ollama_fixed():
    """Fixed Ollama installation with better timeout handling"""
    print_step("Installing Ollama...")
    
    # Check if already installed
    if os.path.exists("C:\\Program Files\\Ollama\\ollama.exe"):
        print_success("Ollama already installed")
        return True
    
    # Download Ollama installer
    installer = "OllamaSetup.exe"
    url = "https://ollama.com/download/OllamaSetup.exe"
    
    if not download_with_progress(url, installer):
        return False
    
    # Run installer - DON'T use timeout, let it run
    print_step("Installing Ollama (this may take a few minutes)...")
    print_warning("DO NOT close the installer window if it appears")
    
    try:
        # Method 1: Try silent install without timeout
        print_step("Attempting silent install...")
        process = subprocess.Popen([installer, "/S"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        
        # Wait for process to complete (no timeout)
        print_step("Waiting for installation to complete...")
        process.wait()
        
        # Check result
        if process.returncode == 0 and os.path.exists("C:\\Program Files\\Ollama\\ollama.exe"):
            print_success("Ollama installed successfully")
            return True
        else:
            print_warning("Silent install may have failed")
            
    except Exception as e:
        print_warning(f"Silent install attempt: {e}")
    
    # Method 2: Interactive install
    print_step("Starting interactive installer...")
    print_warning("Please complete the installation manually:")
    print("  1. Click 'Yes' if UAC prompts")
    print("  2. Click 'Install' in the installer")
    print("  3. Wait for completion")
    
    # Run installer normally
    os.startfile(installer)
    
    # Wait for user
    input(f"\n{colors.yellow('Press Enter AFTER installation is complete...')}")
    
    # Verify installation
    if os.path.exists("C:\\Program Files\\Ollama\\ollama.exe"):
        print_success("Ollama installed successfully")
        return True
    else:
        print_error("Installation failed")
        return False

def start_ollama_service():
    """Start Ollama service with better verification"""
    print_step("Starting Ollama...")
    
    # Kill any existing processes
    os.system("taskkill /F /IM ollama.exe 2>nul")
    os.system("taskkill /F /IM ollama_llama_server.exe 2>nul")
    time.sleep(2)
    
    # Add to PATH
    os.environ["PATH"] += ";C:\\Program Files\\Ollama"
    
    # Start Ollama
    try:
        subprocess.Popen(
            ["C:\\Program Files\\Ollama\\ollama.exe", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Wait for startup with better verification
        print_step("Waiting for Ollama to start...")
        max_wait = 30
        for i in range(max_wait):
            time.sleep(2)
            
            # Test if ollama is responding
            result = os.system("ollama list >nul 2>&1")
            if result == 0:
                print_success("Ollama is running")
                return True
            
            # Also check if process exists
            success, stdout, stderr = run_powershell("Get-Process ollama -ErrorAction SilentlyContinue")
            if success and stdout:
                print(f"  Process running, waiting for API... ({i+1}/{max_wait//2})")
        
        print_warning("Ollama may not be fully responsive")
        return False
        
    except Exception as e:
        print_error(f"Failed to start Ollama: {e}")
        return False

def verify_ollama_installation():
    """Verify Ollama is properly installed"""
    print_step("Verifying Ollama installation...")
    
    # Check executable
    if not os.path.exists("C:\\Program Files\\Ollama\\ollama.exe"):
        print_error("Ollama executable not found")
        return False
    
    # Add to PATH
    os.environ["PATH"] += ";C:\\Program Files\\Ollama"
    
    # Test command
    success, stdout, stderr = run_powershell("ollama --version")
    if success:
        print_success(f"Ollama {stdout.strip()} detected")
        return True
    
    # Try direct path
    result = os.system("C:\\Program Files\\Ollama\\ollama.exe --version >nul 2>&1")
    if result == 0:
        print_success("Ollama executable working")
        return True
    
    print_error("Ollama not responding")
    return False

def download_model_safe(model_name):
    """Download model with proper verification"""
    print_step(f"Downloading DeepSeek-{CONFIG['model_size']} (~19GB)...")
    print_warning("This will take time. DO NOT close this window.")
    
    # First check if model already exists
    success, stdout, stderr = run_powershell("ollama list")
    if success and model_name in stdout:
        print_success(f"Model {model_name} already downloaded")
        return True
    
    try:
        # Run download with real-time output
        process = subprocess.Popen(
            f'ollama pull {model_name}',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Show progress
        for line in process.stdout:
            if "pulling" in line.lower():
                print(f"  {line.strip()}")
            elif "success" in line.lower():
                print_success(line.strip())
            elif "error" in line.lower():
                print_error(line.strip())
            elif "downloading" in line.lower():
                # Show compact progress
                print(f"  {line.strip()}")
        
        process.wait()
        
        if process.returncode == 0:
            print_success(f"Model {model_name} downloaded!")
            return True
        else:
            print_error("Download failed")
            return False
            
    except KeyboardInterrupt:
        print(f"\n{colors.yellow('⚠ Download paused. Run again to resume.')}")
        return False
    except Exception as e:
        print_error(f"Download error: {e}")
        return False

def create_launchers(model_name):
    """Create working launchers"""
    print_step("Creating launcher scripts...")
    
    # Main chat batch file with error checking
    with open("chat.bat", "w") as f:
        f.write(f"""@echo off
title DeepSeek Chat
color 0A
echo.
echo 🚀 Starting DeepSeek Chat...
echo ============================
echo.

:: Add Ollama to PATH
set PATH=%PATH%;C:\\Program Files\\Ollama

:: Check if Ollama is running
echo Checking Ollama...
ollama list >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠ Ollama not responding!
    echo.
    echo Starting Ollama...
    start /b C:\\Program Files\\Ollama\\ollama.exe serve
    timeout /t 5 /nobreak >nul
)

echo.
echo Model: {model_name}
echo Type 'exit' to quit
echo.

:: Start chat
ollama run {model_name}
pause
""")
    
    # Test script with better diagnostics
    with open("test.bat", "w") as f:
        f.write(f"""@echo off
color 0E
echo Testing DeepSeek Installation...
echo ================================
echo.

:: Add Ollama to PATH
set PATH=%PATH%;C:\\Program Files\\Ollama

:: Check Ollama version
echo 1. Checking Ollama installation...
ollama --version
if %errorlevel% neq 0 (
    echo ❌ Ollama not found!
    echo    Make sure it's installed in C:\\Program Files\\Ollama
    pause
    exit /b 1
)
echo ✅ Ollama found
echo.

:: Check if running
echo 2. Checking Ollama service...
ollama list >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Ollama is running
) else (
    echo ⚠ Ollama not responding
    echo    Starting Ollama...
    start /b C:\\Program Files\\Ollama\\ollama.exe serve
    timeout /t 5 /nobreak >nul
)
echo.

:: Check model
echo 3. Checking DeepSeek model...
ollama list | findstr {model_name} >nul
if %errorlevel% equ 0 (
    echo ✅ Model {model_name} is downloaded
) else (
    echo ❌ Model not found!
    echo    Run: ollama pull {model_name}
)
echo.

:: Test model
echo 4. Testing model response...
echo    Sending: "Hello, are you working?"
echo.
echo DeepSeek: | ollama run {model_name} "Hello, are you working?" 2>nul
echo.

if %errorlevel% equ 0 (
    echo ✅ DeepSeek is working!
) else (
    echo ❌ Something went wrong
)

echo.
pause
""")
    
    # PowerShell script
    with open("chat.ps1", "w") as f:
        f.write(f"""$env:Path += ";C:\\Program Files\\Ollama"

Write-Host "🚀 DeepSeek Chat" -ForegroundColor Cyan
Write-Host "Type 'exit' to quit, 'clear' to clear screen" -ForegroundColor Yellow
Write-Host "="*60

# Check Ollama
$ollama = Get-Command ollama -ErrorAction SilentlyContinue
if (-not $ollama) {{
    Write-Host "❌ Ollama not found!" -ForegroundColor Red
    exit
}}

while ($true) {{
    $input = Read-Host "`nYou"
    if ($input -eq "exit") {{ break }}
    if ($input -eq "clear") {{ Clear-Host; continue }}
    
    Write-Host "DeepSeek: " -NoNewline
    $response = & ollama run {model_name} $input 2>$null
    Write-Host $response -ForegroundColor Green
}}
""")
    
    # README with troubleshooting
    with open("README.txt", "w") as f:
        f.write(f"""DEEPSEEK CHAT - QUICK START
==========================

📁 SCRIPTS:
   chat.bat     → Double-click to chat
   test.bat     → Run this FIRST to verify installation
   chat.ps1     → PowerShell version

🚀 FIRST TIME:
   1. Double-click test.bat to verify everything works
   2. If test passes, double-click chat.bat to start chatting

🔧 TROUBLESHOOTING:

If "Ollama not found":
   • Make sure Ollama is installed in C:\\Program Files\\Ollama
   • Restart your computer
   • Run test.bat again

If "Model not found":
   • Open Command Prompt as Administrator
   • Run: ollama pull {model_name}
   • Wait for download to complete

If Ollama not responding:
   • Open Task Manager
   • Kill any ollama.exe processes
   • Run test.bat again

Model: {model_name}
Download size: ~19GB
    """)
    
    print_success("Created launcher scripts:")
    print("  ├─ test.bat  (RUN THIS FIRST)")
    print("  ├─ chat.bat  (double-click to chat)")
    print("  └─ chat.ps1  (PowerShell version)")

def main():
    """Main installation function"""
    print_header("DeepSeek-V3 Installer for Windows")
    print(f"Target model: {CONFIG['model_size']} (~19GB)")
    print()
    
    # Track installation status
    install_success = False
    model_downloaded = False
    
    # Check admin
    if not is_admin():
        print_warning("Not running as Administrator")
        print_warning("Some features may not work")
        response = input("Continue anyway? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            return
    
    # Install Ollama
    if install_ollama_fixed():
        # Verify installation
        if verify_ollama_installation():
            # Start service
            if start_ollama_service():
                install_success = True
                
                # Get model name
                models = {
                    "1.5b": "deepseek-r1:1.5b",
                    "7b": "deepseek-r1:7b",
                    "8b": "deepseek-r1:8b",
                    "14b": "deepseek-r1:14b",
                    "32b": "deepseek-r1:32b",
                    "70b": "deepseek-r1:70b",
                }
                model_name = models.get(CONFIG["model_size"], "deepseek-r1:14b")
                
                # Download model
                if download_model_safe(model_name):
                    model_downloaded = True
                    create_launchers(model_name)
    
    print_header("INSTALLATION RESULTS")
    
    if install_success:
        print_success("✅ Ollama installed successfully!")
    else:
        print_error("❌ Ollama installation failed")
    
    if model_downloaded:
        print_success("✅ Model downloaded successfully!")
    else:
        print_warning("⚠ Model not downloaded")
        print("   Run this manually: ollama pull deepseek-r1:14b")
    
    print(f"""
{colors.cyan('📁 Files created in this folder:')}
   {colors.green('test.bat')}     → Run this FIRST to verify installation
   {colors.green('chat.bat')}     → Double-click to chat (if model is downloaded)
   {colors.green('chat.ps1')}     → PowerShell version
   {colors.green('README.txt')}   → Troubleshooting guide

{colors.yellow('🔧 NEXT STEPS:')}
1. Double-click {colors.green('test.bat')} to verify everything works
2. If model not downloaded, run: {colors.cyan('ollama pull deepseek-r1:14b')}
3. Then double-click {colors.green('chat.bat')} to start

{colors.blue('🚀 For CVE research, start with test.bat first!')}
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{colors.yellow('⚠ Installation cancelled')}")
        sys.exit(0)
