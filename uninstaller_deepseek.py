#!/usr/bin/env python3
"""
DeepSeek Complete Uninstaller
REMOVES everything the installer created
KEEPS itself and the installer script
by nu11secur1ty
Run: python uninstall_complete.py
"""

import os
import sys
import subprocess
import ctypes
import time
import shutil
from pathlib import Path

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

c = Colors()

def print_step(message): print(c.blue(f"➜ {message}"))
def print_success(message): print(c.green(f"✓ {message}"))
def print_warning(message): print(c.yellow(f"⚠ {message}"))
def print_error(message): print(c.red(f"✗ {message}"))
def print_header(message): 
    print(c.cyan("=" * 60))
    print(c.cyan(message.center(60)))
    print(c.cyan("=" * 60))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_command(cmd, timeout=5):
    """Run command with timeout to prevent freezing"""
    try:
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return process.returncode == 0, stdout, stderr
        except subprocess.TimeoutExpired:
            process.kill()
            return False, "", "Timeout"
            
    except:
        return False, "", ""

def stop_ollama():
    """Stop all Ollama processes - FAST"""
    print_step("Stopping Ollama services...")
    
    # Kill processes directly - no waiting
    os.system("taskkill /F /IM ollama.exe 2>nul")
    os.system("taskkill /F /IM ollama_llama_server.exe 2>nul")
    os.system("taskkill /F /IM ollama-service.exe 2>nul")
    
    # Try to stop service but don't wait
    subprocess.Popen("net stop Ollama /y", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(1)
    print_success("Ollama stopped")

def remove_ollama_direct():
    """Remove Ollama DIRECTLY - NO WINGET, NO FREEZING"""
    print_step("Uninstalling Ollama...")
    
    # Kill everything first
    os.system("taskkill /F /IM ollama.exe 2>nul")
    os.system("taskkill /F /IM ollama_llama_server.exe 2>nul")
    os.system("taskkill /F /IM ollama-service.exe 2>nul")
    
    # Run uninstaller if exists (fast, no wait)
    uninstallers = [
        'C:\\Program Files\\Ollama\\Uninstall.exe',
        os.path.expanduser('~\\AppData\\Local\\Programs\\Ollama\\Uninstall.exe'),
    ]
    
    for uninstaller in uninstallers:
        if os.path.exists(uninstaller):
            print_step(f"Found uninstaller, running...")
            # Run and forget - don't wait
            subprocess.Popen(f'"{uninstaller}" /S /VERYSILENT', shell=True)
            time.sleep(2)  # Give it a moment to start
    
    # NOW DELETE EVERYTHING DIRECTLY (this is the key!)
    print_step("Removing Ollama directories...")
    
    ollama_dirs = [
        'C:\\Program Files\\Ollama',
        os.path.expanduser('~\\AppData\\Local\\Ollama'),
        os.path.expanduser('~\\AppData\\Roaming\\Ollama'),
        os.path.expanduser('~\\AppData\\Local\\Programs\\Ollama'),
        os.path.expanduser('~\\AppData\\Local\\Temp\\ollama'),
        os.path.expanduser('~\\.ollama'),
    ]
    
    for dir_path in ollama_dirs:
        if os.path.exists(dir_path):
            try:
                # Try Python's rmtree first
                shutil.rmtree(dir_path, ignore_errors=True)
                print(f"  Removed {os.path.basename(dir_path)}")
            except:
                # Force delete with Windows command
                os.system(f'rmdir /s /q "{dir_path}" 2>nul')
                print(f"  Force removed {os.path.basename(dir_path)}")
    
    # Remove from PATH (simple registry delete)
    print_step("Cleaning PATH...")
    
    # Get current user PATH
    success, stdout, stderr = run_command('reg query HKCU\\Environment /v Path 2>nul')
    if success and stdout:
        for line in stdout.split('\n'):
            if 'Path' in line and 'REG_' in line:
                if 'REG_SZ' in line:
                    current_path = line.split('REG_SZ')[-1].strip()
                    if current_path and 'ollama' in current_path.lower():
                        # Remove Ollama from PATH
                        new_path = ';'.join([p for p in current_path.split(';') if p and 'ollama' not in p.lower()])
                        run_command(f'reg add HKCU\\Environment /v Path /t REG_SZ /d "{new_path}" /f 2>nul')
                        print_success("Cleaned Ollama from PATH")
    
    print_success("Ollama uninstalled")

def remove_models_direct():
    """Remove models by deleting directories directly"""
    print_step("Removing DeepSeek models...")
    
    # Models are stored in these locations
    model_paths = [
        os.path.expanduser('~\\AppData\\Local\\Ollama\\models'),
        os.path.expanduser('~\\AppData\\Roaming\\Ollama\\models'),
        os.path.expanduser('~\\AppData\\Local\\Programs\\Ollama\\models'),
        os.path.expanduser('~\\.ollama\\models'),
    ]
    
    removed = 0
    for path in model_paths:
        if os.path.exists(path):
            try:
                shutil.rmtree(path, ignore_errors=True)
                print(f"  Removed models from {os.path.basename(os.path.dirname(path))}")
                removed += 1
            except:
                os.system(f'rmdir /s /q "{path}" 2>nul')
                removed += 1
    
    if removed > 0:
        print_success("DeepSeek models removed")
    else:
        print_warning("No model directories found")

def remove_created_files():
    """Remove files created by installer (KEEP uninstaller & installer)"""
    print_step("Removing installer-created files...")
    
    current_dir = os.getcwd()
    
    # Files to DELETE
    files_to_remove = [
        'chat.bat', 'test.bat', 'chat.ps1',
        'chat_deepseek.bat', 'chat_with_deepseek.ps1',
        'chat_gui.py', 'start_webui.bat',
        'README_WINDOWS.txt', 'README.txt',
        'OllamaSetup.exe', 'DockerSetup.exe',
        'ollama_path.bat', 'test_deepseek.bat',
    ]
    
    # Files to KEEP
    keep_files = [
        'install_deepseek.py',
        'uninstall_complete.py',
    ]
    
    removed = 0
    for file in files_to_remove:
        file_path = os.path.join(current_dir, file)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  Removed {file}")
                removed += 1
            except:
                pass
    
    if removed > 0:
        print_success(f"Removed {removed} file(s)")
    
    # Show kept files
    kept = [f for f in keep_files if os.path.exists(os.path.join(current_dir, f))]
    if kept:
        print_step(f"Keeping: {', '.join(kept)}")

def clean_registry_fast():
    """Quick registry cleanup"""
    print_step("Cleaning registry...")
    
    reg_paths = [
        'HKCU\\SOFTWARE\\Ollama',
        'HKLM\\SOFTWARE\\Ollama',
        'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Ollama',
    ]
    
    for reg_path in reg_paths:
        os.system(f'reg delete "{reg_path}" /f 2>nul')

def verify_uninstall():
    """Quick verification"""
    print_step("Verifying uninstallation...")
    
    issues = []
    
    # Quick checks
    if os.path.exists('C:\\Program Files\\Ollama'):
        issues.append("Ollama folder still exists")
    
    model_paths = [
        os.path.expanduser('~\\AppData\\Local\\Ollama'),
        os.path.expanduser('~\\.ollama'),
    ]
    
    for path in model_paths:
        if os.path.exists(path):
            issues.append(f"{os.path.basename(path)} still exists")
    
    if issues:
        print_warning("Some components may still exist:")
        for issue in issues:
            print(f"  • {issue}")
        
        # Force cleanup
        response = input(f"{c.yellow('Force remove remaining items? (y/N): ')}")
        if response.lower() in ['y', 'yes']:
            os.system('rmdir /s /q "C:\\Program Files\\Ollama" 2>nul')
            os.system(f'rmdir /s /q "{os.path.expanduser("~\\AppData\\Local\\Ollama")}" 2>nul')
            os.system(f'rmdir /s /q "{os.path.expanduser("~\\.ollama")}" 2>nul')
            print_success("Force cleaned")
    else:
        print_success("✓ All DeepSeek components removed!")

def main():
    """Main uninstall function"""
    print_header("DeepSeek Complete Uninstaller")
    print(f"""
{c.yellow('This will REMOVE:')}
  • Ollama completely
  • All DeepSeek models
  • Configuration files
  • chat.bat, test.bat, etc.

{c.green('This will KEEP:')}
  • {os.path.basename(__file__)} (this uninstaller)
  • install_deepseek.py (the installer)
    """)
    
    response = input(f"{c.yellow('Continue? (yes/NO): ')}")
    if response.lower() not in ['yes', 'y']:
        print_success("Cancelled")
        return
    
    if not is_admin():
        print_warning("Not running as Administrator")
        response = input(f"{c.yellow('Continue anyway? (y/N): ')}")
        if response.lower() not in ['y', 'yes']:
            return
    
    print_header("Starting uninstall")
    
    # DO EVERYTHING FAST - NO WAITING
    stop_ollama()
    remove_models_direct()  # Delete models directly
    remove_ollama_direct()  # Delete Ollama directly (NO WINGET!)
    remove_created_files()  # Remove created files
    clean_registry_fast()   # Quick registry clean
    
    # Verify
    verify_uninstall()
    
    print_header("UNINSTALL COMPLETE")
    print(f"""
{c.green('✅ DeepSeek has been removed!')}

{c.cyan('📁 Kept:')}
   • {os.path.basename(__file__)}
   • install_deepseek.py

{c.yellow('💡 Restart your computer to complete')}
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{c.yellow('⚠ Cancelled')}")
        sys.exit(0)
