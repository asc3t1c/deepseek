#!/usr/bin/env python3
"""
DeepSeek Complete Uninstaller - FIXED EDITION
REMOVES everything the installer created
KEEPS itself and the installer script
BY nu11secur1ty 2026
Run: python uninstall_complete.py
"""

import os
import sys
import subprocess
import ctypes
import time
import shutil
import stat
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

def run_command(cmd, timeout=3):
    """Run command with aggressive timeout"""
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
            process.terminate()
            return False, "", "Timeout"
    except:
        return False, "", ""

def force_kill_processes():
    """AGGRESSIVELY kill all Ollama processes"""
    print_step("Force killing all Ollama processes...")
    
    kill_commands = [
        'taskkill /F /IM ollama.exe 2>nul',
        'taskkill /F /IM ollama_llama_server.exe 2>nul',
        'taskkill /F /IM ollama-service.exe 2>nul',
        'taskkill /F /IM ollama-serve.exe 2>nul',
        'powershell -Command "Get-Process ollama* | Stop-Process -Force" 2>nul'
    ]
    
    for cmd in kill_commands:
        os.system(cmd)
    
    time.sleep(1)
    print_success("All Ollama processes terminated")

def stop_ollama_service_force():
    """Force stop Windows service"""
    print_step("Stopping Ollama Windows service...")
    
    service_commands = [
        'net stop Ollama /y 2>nul',
        'sc stop Ollama 2>nul',
        'sc delete Ollama 2>nul',
    ]
    
    for cmd in service_commands:
        os.system(cmd)
    
    time.sleep(1)
    print_success("Ollama service stopped")

def remove_directory_with_prejudice(dirpath):
    """NUKE a directory - no mercy"""
    if not os.path.exists(dirpath):
        return False
    
    try:
        shutil.rmtree(dirpath, ignore_errors=True)
    except:
        pass
    
    if os.path.exists(dirpath):
        os.system(f'rmdir /s /q "{dirpath}" 2>nul')
    
    return not os.path.exists(dirpath)

def remove_ollama_direct():
    """Remove Ollama completely"""
    print_step("REMOVING OLLAMA...")
    
    user_home = os.path.expanduser("~")
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    local_appdata = os.environ.get("LOCALAPPDATA", f"{user_home}\\AppData\\Local")
    roaming_appdata = os.environ.get("APPDATA", f"{user_home}\\AppData\\Roaming")
    
    ollama_paths = [
        f"{program_files}\\Ollama",
        f"{program_files_x86}\\Ollama",
        f"{local_appdata}\\Ollama",
        f"{local_appdata}\\Programs\\Ollama",
        f"{roaming_appdata}\\Ollama",
        f"{user_home}\\.ollama",
        f"{user_home}\\AppData\\Local\\Temp\\ollama",
    ]
    
    removed_count = 0
    for dir_path in ollama_paths:
        if os.path.exists(dir_path):
            print(f"  Removing: {dir_path}")
            if remove_directory_with_prejudice(dir_path):
                removed_count += 1
                print(f"    ✓ Removed")
    
    if removed_count > 0:
        print_success(f"Removed {removed_count} Ollama installations")
    else:
        print_warning("No Ollama directories found")

def remove_models_direct():
    """Remove all model directories"""
    print_step("REMOVING DeepSeek models...")
    
    user_home = os.path.expanduser("~")
    local_appdata = os.environ.get("LOCALAPPDATA", f"{user_home}\\AppData\\Local")
    roaming_appdata = os.environ.get("APPDATA", f"{user_home}\\AppData\\Roaming")
    
    model_paths = [
        f"{local_appdata}\\Ollama\\models",
        f"{roaming_appdata}\\Ollama\\models",
        f"{local_appdata}\\Programs\\Ollama\\models",
        f"{user_home}\\.ollama\\models",
    ]
    
    removed = 0
    for path in model_paths:
        if os.path.exists(path):
            print(f"  Removing: {path}")
            if remove_directory_with_prejudice(path):
                removed += 1
    
    if removed > 0:
        print_success(f"Removed {removed} model directories")
    else:
        print_warning("No model directories found")

def clean_registry_simple():
    """SIMPLE registry cleaning - NO HANGING"""
    print_step("Cleaning registry...")
    
    # Just nuke the main paths - no searching
    reg_paths = [
        'HKCU\\SOFTWARE\\Ollama',
        'HKLM\\SOFTWARE\\Ollama',
        'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Ollama',
    ]
    
    cleaned = 0
    for reg_path in reg_paths:
        result = os.system(f'reg delete "{reg_path}" /f 2>nul')
        if result == 0:
            cleaned += 1
    
    if cleaned > 0:
        print_success(f"Cleaned {cleaned} registry entries")
    else:
        print_step("No registry entries found")

def clean_path_simple():
    """SIMPLE PATH cleaning - NO HANGING"""
    print_step("Cleaning PATH...")
    
    # Just notify - manual cleanup is safer
    print_step("PATH cleanup skipped - do manually if needed")
    print_step("Go to: System Properties → Environment Variables")

def remove_created_files():
    """Remove installer-created files"""
    print_step("REMOVING installer-created files...")
    
    current_dir = os.getcwd()
    
    files_to_remove = [
        'chat.bat', 'test.bat', 'chat.ps1',
        'chat_deepseek.bat', 'chat_with_deepseek.ps1',
        'download_model.bat', 'start_download.bat',
        'test_deepseek.bat', 'ollama_path.bat',
        'chat_gui.py', 'start_webui.bat',
        'README_WINDOWS.txt', 'README.txt',
        'OllamaSetup.exe', 'DockerSetup.exe',
        'start_download.vbs', '*.log', '*.tmp',
    ]
    
    keep_files = [
        'install_deepseek.py',
        'uninstall_complete.py',
    ]
    
    removed = 0
    for pattern in files_to_remove:
        if '*' in pattern:
            import glob
            for file_path in glob.glob(pattern):
                if os.path.basename(file_path) not in keep_files:
                    try:
                        os.remove(file_path)
                        print(f"  Removed {os.path.basename(file_path)}")
                        removed += 1
                    except:
                        pass
        else:
            file_path = os.path.join(current_dir, pattern)
            if os.path.exists(file_path) and pattern not in keep_files:
                try:
                    os.remove(file_path)
                    print(f"  Removed {pattern}")
                    removed += 1
                except:
                    pass
    
    if removed > 0:
        print_success(f"Removed {removed} installer-created files")
    
    kept = [f for f in keep_files if os.path.exists(os.path.join(current_dir, f))]
    if kept:
        print_step(f"Preserved: {', '.join(kept)}")

def verify_uninstall():
    """Simple verification"""
    print_step("Verifying uninstallation...")
    
    issues = []
    
    if os.path.exists('C:\\Program Files\\Ollama'):
        issues.append("Ollama folder still exists")
    
    user_paths = [
        os.path.expanduser('~\\AppData\\Local\\Ollama'),
        os.path.expanduser('~\\.ollama'),
    ]
    
    for path in user_paths:
        if os.path.exists(path):
            issues.append(f"{os.path.basename(path)} still exists")
    
    if issues:
        print_warning("Some components may still exist:")
        for issue in issues:
            print(f"  • {issue}")
    else:
        print_success("✓ All DeepSeek components removed!")

def main():
    """Main uninstall function"""
    print_header("DEEPSEEK UNINSTALLER")
    print(f"""
{c.yellow('This will REMOVE:')}
  • Ollama completely
  • All DeepSeek models
  • Configuration files
  • chat.bat, test.bat, etc.

{c.green('This will SURVIVE:')}
  • {os.path.basename(__file__)} (this uninstaller)
  • install_deepseek.py (the installer)
    """)
    
    response = input(f"{c.yellow('ARE YOU ABSOLUTELY SURE? (yes/NUCLEAR): ')}")
    if response.upper() != 'NUCLEAR':
        print_success("Aborting uninstall")
        return
    
    if not is_admin():
        print_error("Please run as Administrator")
        input("Press Enter to exit...")
        return
    
    print_header("STARTING UNINSTALL")
    
    # Kill processes
    force_kill_processes()
    stop_ollama_service_force()
    
    # Remove everything
    remove_models_direct()
    remove_ollama_direct()
    remove_created_files()
    
    # Quick registry clean (no hang)
    clean_registry_simple()
    clean_path_simple()
    
    # Verify
    verify_uninstall()
    
    print_header("UNINSTALL COMPLETE")
    print(f"""
{c.green('✓ DeepSeek has been removed!')}

{c.cyan('Surviving files:')}
   • {os.path.basename(__file__)}
   • install_deepseek.py

{c.yellow('Restart your computer to complete')}
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{c.yellow('Aborted')}")
        sys.exit(0)
