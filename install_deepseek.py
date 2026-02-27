#!/usr/bin/env python3
"""
DeepSeek-V3 Fixed Installer for Windows 11 Pro
WITH 32B UNCENSORED MODEL FROM f0rc3ps- nu11secur1ty REPOSITORY
BY nu11secur1ty 2026
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

# Configuration - UPDATED TO YOUR REPO!
CONFIG = {
    "model_name": "f0rc3ps/deepseek-r1-32b-uncensored",  # YOUR model!
    "model_size": "32b",
    "repo_url": "https://ollama.com/f0rc3ps/deepseek-r1-32b-uncensored",
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
    """FIXED Ollama installation - SIMPLIFIED"""
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
    
    # SIMPLE APPROACH: Just run the installer normally and let user click
    print_step("Starting Ollama installer...")
    print_warning("PLEASE FOLLOW THESE STEPS:")
    print("  1. Click 'Yes' if Windows asks for permission")
    print("  2. Click 'Install' in the installer window")
    print("  3. Wait for the installation to finish")
    print("  4. The installer window will close automatically")
    print()
    
    # Run installer normally (not silent)
    os.startfile(installer)
    
    # Wait for user to complete
    input(f"\n{colors.yellow('PRESS ENTER AFTER INSTALLATION IS COMPLETE...')}")
    
    # FIX: Check multiple possible locations for Ollama
    ollama_paths = [
        "C:\\Program Files\\Ollama\\ollama.exe",
        "C:\\Program Files (x86)\\Ollama\\ollama.exe",
        os.path.expanduser("~\\AppData\\Local\\Programs\\Ollama\\ollama.exe"),
        os.path.expanduser("~\\AppData\\Local\\Ollama\\ollama.exe")
    ]
    
    ollama_found = False
    for path in ollama_paths:
        if os.path.exists(path):
            ollama_found = True
            print_success(f"Ollama found at: {path}")
            break
    
    # Also check if ollama command works in PATH
    if not ollama_found:
        result = os.system("ollama --version >nul 2>&1")
        if result == 0:
            ollama_found = True
            print_success("Ollama found in PATH")
    
    if ollama_found:
        print_success("Ollama installed successfully!")
        return True
    else:
        print_error("Installation failed - Ollama not found")
        print("Try installing manually from: https://ollama.com/download/windows")
        return False

def start_ollama_service():
    """Start Ollama service"""
    print_step("Starting Ollama...")
    
    # Kill any existing processes
    os.system("taskkill /F /IM ollama.exe 2>nul")
    os.system("taskkill /F /IM ollama_llama_server.exe 2>nul")
    time.sleep(2)
    
    # Add common Ollama paths to PATH
    ollama_paths = [
        "C:\\Program Files\\Ollama",
        "C:\\Program Files (x86)\\Ollama",
        os.path.expanduser("~\\AppData\\Local\\Programs\\Ollama"),
        os.path.expanduser("~\\AppData\\Local\\Ollama")
    ]
    
    for path in ollama_paths:
        if os.path.exists(path):
            os.environ["PATH"] += f";{path}"
    
    # Find ollama executable
    ollama_exe = None
    for path in ollama_paths:
        exe_path = os.path.join(path, "ollama.exe")
        if os.path.exists(exe_path):
            ollama_exe = exe_path
            break
    
    if not ollama_exe:
        # Try to find in PATH
        import shutil
        ollama_exe = shutil.which("ollama")
    
    if not ollama_exe:
        print_error("Cannot find ollama executable")
        return False
    
    # Start Ollama
    try:
        subprocess.Popen(
            [ollama_exe, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        print_step("Waiting for Ollama to start...")
        for i in range(15):
            time.sleep(2)
            result = os.system("ollama list >nul 2>&1")
            if result == 0:
                print_success("Ollama is running")
                return True
            print(f"  Still waiting... ({i+1}/15)")
        
        print_warning("Ollama may not be fully responsive")
        return True
        
    except Exception as e:
        print_error(f"Failed to start Ollama: {e}")
        return False

def verify_ollama_installation():
    """Verify Ollama is installed"""
    print_step("Verifying Ollama installation...")
    
    # Check multiple locations
    ollama_paths = [
        "C:\\Program Files\\Ollama\\ollama.exe",
        "C:\\Program Files (x86)\\Ollama\\ollama.exe",
        os.path.expanduser("~\\AppData\\Local\\Programs\\Ollama\\ollama.exe"),
        os.path.expanduser("~\\AppData\\Local\\Ollama\\ollama.exe")
    ]
    
    ollama_found = False
    for path in ollama_paths:
        if os.path.exists(path):
            ollama_found = True
            # Add to PATH
            os.environ["PATH"] += f";{os.path.dirname(path)}"
            print_success(f"Ollama found at: {path}")
            break
    
    # Also check PATH
    if not ollama_found:
        result = os.system("ollama --version >nul 2>&1")
        if result == 0:
            ollama_found = True
            print_success("Ollama found in PATH")
    
    if ollama_found:
        return True
    else:
        print_error("Ollama executable not found")
        return False

def download_model_safe():
    """Download YOUR 32B uncensored model from f0rc3ps repo"""
    model_name = CONFIG["model_name"]
    print_header(f"Downloading from YOUR repository")
    print(f"Model: {model_name}")
    print(f"Repo: {CONFIG['repo_url']}")
    print(f"Size: 19GB")
    print()
    
    # Check if already downloaded
    result = os.system(f"ollama list | findstr f0rc3ps >nul 2>&1")
    if result == 0:
        print_success(f"Model {model_name} already downloaded")
        return True
    
    print_step(f"Pulling f0rc3ps/deepseek-r1-32b-uncensored...")
    print_warning("This will take 20-60 minutes. DO NOT close this window!")
    print()
    
    try:
        # Simple download - let it show progress naturally
        process = subprocess.Popen(
            f'ollama pull {model_name}',
            shell=True
        )
        process.wait()
        
        if process.returncode == 0:
            print_success(f"Model downloaded successfully from f0rc3ps repository!")
            return True
        else:
            print_error("Download failed")
            return False
            
    except KeyboardInterrupt:
        print(f"\n{colors.yellow('⚠ Download cancelled')}")
        return False
    except Exception as e:
        print_error(f"Download error: {e}")
        return False

def create_launchers():
    """Create launcher scripts - WITH YOUR REPO CREDITS"""
    model_name = CONFIG["model_name"]
    repo_url = CONFIG["repo_url"]
    print_step("Creating launcher scripts...")
    
    with open("chat.bat", "w", encoding='utf-8') as f:
        f.write(f"""@echo off
title DeepSeek 32B Uncensored - f0rc3ps Repo
color 0A
echo.
echo ====== DeepSeek 32B Uncensored ======
echo ====== from f0rc3ps repository ======
echo.
set PATH=%PATH%;C:\\Program Files\\Ollama;C:\\Program Files (x86)\\Ollama;%USERPROFILE%\\AppData\\Local\\Programs\\Ollama;%USERPROFILE%\\AppData\\Local\\Ollama
echo Model: {model_name}
echo Repo: {repo_url}
echo Type 'exit' to quit
echo.
ollama run {model_name}
pause
""")
    
    with open("test.bat", "w", encoding='utf-8') as f:
        f.write(f"""@echo off
color 0E
echo Testing DeepSeek 32B Uncensored - f0rc3ps Repo
echo =============================================
echo.
set PATH=%PATH%;C:\\Program Files\\Ollama;C:\\Program Files (x86)\\Ollama;%USERPROFILE%\\AppData\\Local\\Programs\\Ollama;%USERPROFILE%\\AppData\\Local\\Ollama
echo 1. Ollama version:
ollama --version
echo.
echo 2. Your model:
ollama list | findstr f0rc3ps
echo.
echo 3. Quick test:
echo "Hello from f0rc3ps repo!" | ollama run {model_name}
echo.
if %errorlevel% equ 0 (
    echo [SUCCESS] Your model is working!
) else (
    echo [ERROR] Something went wrong
)
pause
""")
    
    # Create auto-download script for after installer closes
    with open("download_model.bat", "w", encoding='utf-8') as f:
        f.write(f"""@echo off
echo Downloading DeepSeek 32B Uncensored model from f0rc3ps repo...
echo ============================================================
echo.
set PATH=%PATH%;C:\\Program Files\\Ollama;C:\\Program Files (x86)\\Ollama;%USERPROFILE%\\AppData\\Local\\Programs\\Ollama;%USERPROFILE%\\AppData\\Local\\Ollama
ollama pull {model_name}
echo.
echo Download complete! You can now use chat.bat
pause
""")
    
    print_success("Created launcher scripts with YOUR repository:")
    print("  - test.bat")
    print("  - chat.bat")
    print("  - download_model.bat")

def create_autostart_script():
    """Create a script that runs automatically after installer"""
    with open("start_download.vbs", "w", encoding='utf-8') as f:
        f.write(f"""CreateObject("Wscript.Shell").Run "cmd /c download_model.bat", 0, False
""")
    
    with open("start_download.bat", "w", encoding='utf-8') as f:
        f.write(f"""@echo off
start /b download_model.bat
echo Download started in background window
exit
""")

def main():
    """Main installation function"""
    print_header("DeepSeek 32B Uncensored Installer")
    print(f"Model: {CONFIG['model_name']}")
    print(f"Repository: {CONFIG['repo_url']}")
    print(f"Size: 19GB - Perfect for security research!")
    print()
    
    ollama_installed = False
    
    if not is_admin():
        print_warning("Not running as Administrator")
        response = input("Continue anyway? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            return
    
    # Step 1: Install Ollama
    if install_ollama_fixed():
        ollama_installed = True
        
        # Step 2: Verify and start
        if verify_ollama_installation():
            start_ollama_service()
    
    # ALWAYS create scripts
    create_launchers()
    create_autostart_script()
    
    # Step 3: Download YOUR model
    if ollama_installed:
        download_model_safe()
    
    print_header("INSTALLATION RESULTS")
    
    if ollama_installed:
        print_success("Ollama installed successfully!")
    else:
        if verify_ollama_installation():
            print_success("Ollama detected (installation succeeded)!")
            ollama_installed = True
        else:
            print_error("Ollama installation failed")
            print("   Please install manually from: https://ollama.com/download/windows")
    
    print(f"""
{colors.cyan('Files created:')}
   {colors.green('test.bat')}           -> Test YOUR model
   {colors.green('chat.bat')}           -> Chat with YOUR model
   {colors.green('download_model.bat')} -> Download YOUR 19GB model
   {colors.green('start_download.vbs')} -> Silent background download

{colors.yellow('YOUR REPOSITORY:')}
   {colors.green(CONFIG['repo_url'])}

{colors.yellow('NEXT STEPS:')}
1. {colors.green('DOUBLE-CLICK download_model.bat')} to start downloading YOUR model
2. Wait 20-60 minutes for download to complete
3. Double-click {colors.green('chat.bat')} to start chatting

{colors.blue('For CVE research - YOUR model has NO FILTERS!')}
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{colors.yellow('Installation cancelled')}")
        sys.exit(0)
