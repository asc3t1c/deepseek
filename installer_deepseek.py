#!/usr/bin/env python3
"""
DeepSeek-V3 Fixed Installer for Windows 11 Pro
WITH 32B UNCENSORED MODEL FOR SECURITY RESEARCH
by nu11secur1ty
Run: python install_deepseek.py
"""

import os
import sys
import subprocess
import time
import ctypes
import urllib.request
import winreg
from pathlib import Path

# Configuration - UPDATED TO 32B UNCENSORED
CONFIG = {
    "model_name": "richardyoung/deepseek-r1-32b-uncensored",  # 19GB uncensored model
    "model_size": "32b",     # For display purposes
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
        
        downloaded = 0
        if os.path.exists(filename):
            downloaded = os.path.getsize(filename)
            print(f"  Resuming from {downloaded/(1024*1024):.1f}MB")
        
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
    
    if os.path.exists("C:\\Program Files\\Ollama\\ollama.exe"):
        print_success("Ollama already installed")
        return True
    
    installer = "OllamaSetup.exe"
    url = "https://ollama.com/download/OllamaSetup.exe"
    
    if not download_with_progress(url, installer):
        return False
    
    print_step("Installing Ollama (this may take a few minutes)...")
    print_warning("DO NOT close the installer window if it appears")
    
    try:
        print_step("Attempting silent install...")
        process = subprocess.Popen([installer, "/S"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE)
        
        print_step("Waiting for installation to complete...")
        process.wait()
        
        if process.returncode == 0 and os.path.exists("C:\\Program Files\\Ollama\\ollama.exe"):
            print_success("Ollama installed successfully")
            return True
        else:
            print_warning("Silent install may have failed")
            
    except Exception as e:
        print_warning(f"Silent install attempt: {e}")
    
    print_step("Starting interactive installer...")
    print_warning("Please complete the installation manually:")
    print("  1. Click 'Yes' if UAC prompts")
    print("  2. Click 'Install' in the installer")
    print("  3. Wait for completion")
    
    os.startfile(installer)
    input(f"\n{colors.yellow('Press Enter AFTER installation is complete...')}")
    
    if os.path.exists("C:\\Program Files\\Ollama\\ollama.exe"):
        print_success("Ollama installed successfully")
        return True
    else:
        print_error("Installation failed")
        return False

def start_ollama_service():
    """Start Ollama service with better verification"""
    print_step("Starting Ollama...")
    
    os.system("taskkill /F /IM ollama.exe 2>nul")
    os.system("taskkill /F /IM ollama_llama_server.exe 2>nul")
    time.sleep(2)
    
    os.environ["PATH"] += ";C:\\Program Files\\Ollama"
    
    try:
        subprocess.Popen(
            ["C:\\Program Files\\Ollama\\ollama.exe", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        print_step("Waiting for Ollama to start...")
        max_wait = 30
        for i in range(max_wait):
            time.sleep(2)
            
            result = os.system("ollama list >nul 2>&1")
            if result == 0:
                print_success("Ollama is running")
                return True
            
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
    
    if not os.path.exists("C:\\Program Files\\Ollama\\ollama.exe"):
        print_error("Ollama executable not found")
        return False
    
    os.environ["PATH"] += ";C:\\Program Files\\Ollama"
    
    success, stdout, stderr = run_powershell("ollama --version")
    if success:
        print_success(f"Ollama {stdout.strip()} detected")
        return True
    
    result = os.system("C:\\Program Files\\Ollama\\ollama.exe --version >nul 2>&1")
    if result == 0:
        print_success("Ollama executable working")
        return True
    
    print_error("Ollama not responding")
    return False

def download_model_safe():
    """Download the 32B uncensored model"""
    model_name = CONFIG["model_name"]
    print_step(f"Downloading {model_name} (19GB uncensored model)...")
    print_warning("This will take time. DO NOT close this window.")
    print_warning("Perfect for security research and CVE exploitation!")
    
    success, stdout, stderr = run_powershell("ollama list")
    if success and model_name in stdout:
        print_success(f"Model {model_name} already downloaded")
        return True
    
    try:
        process = subprocess.Popen(
            f'ollama pull {model_name}',
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        for line in process.stdout:
            if "pulling" in line.lower():
                print(f"  {line.strip()}")
            elif "success" in line.lower():
                print_success(line.strip())
            elif "error" in line.lower():
                print_error(line.strip())
            elif "downloading" in line.lower():
                print(f"  {line.strip()}")
        
        process.wait()
        
        if process.returncode == 0:
            print_success(f"Model downloaded successfully!")
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

def create_launchers():
    """Create launcher scripts with the uncensored model"""
    model_name = CONFIG["model_name"]
    print_step("Creating launcher scripts...")
    
    with open("chat.bat", "w") as f:
        f.write(f"""@echo off
title DeepSeek 32B Uncensored
color 0A
echo.
echo 🚀 Starting DeepSeek 32B Uncensored (19GB)...
echo ==========================================
echo.

set PATH=%PATH%;C:\\Program Files\\Ollama

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

ollama run {model_name}
pause
""")
    
    with open("test.bat", "w") as f:
        f.write(f"""@echo off
color 0E
echo Testing DeepSeek 32B Uncensored...
echo =================================
echo.

set PATH=%PATH%;C:\\Program Files\\Ollama

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

echo 3. Checking DeepSeek model...
ollama list | findstr "deepseek" >nul
if %errorlevel% equ 0 (
    echo ✅ Model is downloaded
) else (
    echo ❌ Model not found!
    echo    Run: ollama pull {model_name}
)
echo.

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
    
    with open("README.txt", "w") as f:
        f.write(f"""DEEPSEEK 32B UNCENSORED - FOR SECURITY RESEARCH
=============================================

Model: {model_name}
Size: 19GB
Type: Uncensored - No content filters!

📁 SCRIPTS:
   test.bat  → Run this FIRST to verify installation
   chat.bat  → Double-click to start chatting

🚀 FIRST TIME:
   1. Double-click test.bat
   2. If test passes, double-click chat.bat

🔧 TROUBLESHOOTING:
   • If model not found: ollama pull {model_name}
   • If Ollama not responding: restart your computer

⚠️ NOTE: This is an uncensored model - no refusal behavior!
         Perfect for CVE research and exploit development.
""")
    
    print_success("Created launcher scripts:")
    print("  ├─ test.bat  (RUN THIS FIRST)")
    print("  └─ chat.bat  (double-click to chat)")

def main():
    """Main installation function"""
    print_header("DeepSeek 32B Uncensored Installer")
    print(f"Model: {CONFIG['model_name']}")
    print(f"Size: 19GB - Perfect for security research!")
    print()
    
    install_success = False
    model_downloaded = False
    
    if not is_admin():
        print_warning("Not running as Administrator")
        response = input("Continue anyway? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            return
    
    if install_ollama_fixed():
        if verify_ollama_installation():
            if start_ollama_service():
                install_success = True
                
                if download_model_safe():
                    model_downloaded = True
                    create_launchers()
    
    print_header("INSTALLATION RESULTS")
    
    if install_success:
        print_success("✅ Ollama installed successfully!")
    else:
        print_error("❌ Ollama installation failed")
    
    if model_downloaded:
        print_success("✅ 32B Uncensored model downloaded!")
    else:
        print_warning("⚠ Model not downloaded")
        print(f"   Run manually: ollama pull {CONFIG['model_name']}")
    
    print(f"""
{colors.cyan('📁 Files created:')}
   {colors.green('test.bat')}  → Run this FIRST
   {colors.green('chat.bat')}  → Start chatting
   {colors.green('README.txt')} → Info

{colors.yellow('🔧 NEXT STEPS:')}
1. Double-click {colors.green('test.bat')} to verify
2. Then double-click {colors.green('chat.bat')} to start

{colors.blue('🚀 For CVE research, this uncensored model has no filters!')}
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{colors.yellow('⚠ Installation cancelled')}")
        sys.exit(0)
