#!/usr/bin/env python3
"""
DeepSeek 32B Uncensored Installer - f0rc3ps Repository
BY nu11secur1ty 2026
Run: python install_deepseek.py
"""

import os
import sys
import subprocess
import time
import ctypes
import urllib.request

# Configuration
CONFIG = {
    "model_name": "f0rc3ps/deepseek-r1-32b-uncensored",
    "model_size": "32b",
    "repo_url": "https://ollama.com/f0rc3ps/deepseek-r1-32b-uncensored",
}

# Windows-compatible colors
class Colors:
    def __init__(self):
        self.enabled = any([os.environ.get('WT_SESSION'), 
                           os.environ.get('TERM_PROGRAM') == 'vscode'])
    
    def green(self, text): return f"\033[92m{text}\033[0m" if self.enabled else text
    def yellow(self, text): return f"\033[93m{text}\033[0m" if self.enabled else text
    def red(self, text): return f"\033[91m{text}\033[0m" if self.enabled else text
    def blue(self, text): return f"\033[94m{text}\033[0m" if self.enabled else text
    def cyan(self, text): return f"\033[96m{text}\033[0m" if self.enabled else text

c = Colors()

def print_step(msg): print(c.blue(f"➜ {msg}"))
def print_success(msg): print(c.green(f"✓ {msg}"))
def print_warning(msg): print(c.yellow(f"⚠ {msg}"))
def print_error(msg): print(c.red(f"✗ {msg}"))
def print_header(msg): 
    print(c.cyan("=" * 60))
    print(c.cyan(msg.center(60)))
    print(c.cyan("=" * 60))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

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
            
            with open(filename, 'ab' if downloaded > 0 else 'wb') as f:
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
        
        print(f"\n{c.green('✓ Download complete!')}")
        return True
        
    except KeyboardInterrupt:
        print(f"\n{c.yellow('⚠ Download paused. Run again to resume.')}")
        return False
    except Exception as e:
        print_error(f"Download failed: {e}")
        return False

def install_ollama():
    """Install Ollama"""
    print_step("Installing Ollama...")
    
    if os.path.exists("C:\\Program Files\\Ollama\\ollama.exe"):
        print_success("Ollama already installed")
        return True
    
    if not download_with_progress("https://ollama.com/download/OllamaSetup.exe", "OllamaSetup.exe"):
        return False
    
    print_step("Starting Ollama installer...")
    print_warning("Click 'Install' when prompted")
    os.startfile("OllamaSetup.exe")
    input(f"\n{c.yellow('Press Enter AFTER installation completes...')}")
    
    if os.path.exists("C:\\Program Files\\Ollama\\ollama.exe"):
        print_success("Ollama installed")
        return True
    
    print_error("Installation failed")
    return False

def start_ollama():
    """Start Ollama"""
    print_step("Starting Ollama...")
    
    os.system("taskkill /F /IM ollama.exe 2>nul")
    time.sleep(2)
    
    os.environ["PATH"] += ";C:\\Program Files\\Ollama"
    
    subprocess.Popen(["C:\\Program Files\\Ollama\\ollama.exe", "serve"], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW)
    
    print_step("Waiting for Ollama to start...")
    for i in range(10):
        time.sleep(2)
        if os.system("ollama list >nul 2>&1") == 0:
            print_success("Ollama is running")
            return True
        print(f"  Waiting... ({i+1}/10)")
    
    return True

def download_model():
    """Download YOUR model with progress"""
    print_header(f"Downloading YOUR model")
    print(f"Model: {c.green(CONFIG['model_name'])}")
    print(f"Repo: {c.cyan(CONFIG['repo_url'])}")
    print(f"Size: 19GB")
    print()
    
    # Check if already downloaded
    if os.system(f"ollama list | findstr f0rc3ps >nul 2>&1") == 0:
        print_success("Model already downloaded")
        return True
    
    print_step("Starting download...")
    print_warning("This will take 20-60 minutes")
    print()
    
    process = subprocess.Popen(f'ollama pull {CONFIG["model_name"]}', shell=True)
    process.wait()
    
    if process.returncode == 0:
        print_success("✓ Model downloaded successfully!")
        return True
    else:
        print_error("Download failed")
        return False

def main():
    print_header("DeepSeek 32B Uncensored Installer")
    print(f"Model: {c.green(CONFIG['model_name'])}")
    print(f"Repo: {c.cyan(CONFIG['repo_url'])}")
    print()
    
    if not is_admin():
        print_warning("Not running as Administrator")
        if input("Continue? (y/N): ").lower() not in ['y', 'yes']:
            return
    
    if install_ollama():
        start_ollama()
        if download_model():
            print_header("INSTALLATION COMPLETE")
            print(f"\n{c.green('✓ YOUR model is ready!')}")
            print(f"\n{c.cyan('Run it with:')}")
            print(f"  ollama run {CONFIG['model_name']}")
            print(f"\n{c.yellow('No .bat files, no .vbs, no baloney!')}")
    
    print_header("nu11secur1ty 2026")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{c.yellow('Cancelled')}")
        sys.exit(0)
