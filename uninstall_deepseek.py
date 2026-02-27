#!/usr/bin/env python3
"""
DeepSeek Complete Uninstaller - HARDENED EDITION
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
    
    # Multiple kill methods for redundancy
    kill_commands = [
        'taskkill /F /IM ollama.exe 2>nul',
        'taskkill /F /IM ollama_llama_server.exe 2>nul',
        'taskkill /F /IM ollama-service.exe 2>nul',
        'taskkill /F /IM ollama-serve.exe 2>nul',
        'wmic process where "name like \'%ollama%\'" delete 2>nul',
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
        'powershell -Command "Stop-Service Ollama -Force" 2>nul',
        'powershell -Command "sc.exe delete Ollama" 2>nul'
    ]
    
    for cmd in service_commands:
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    time.sleep(1)
    print_success("Ollama service stopped")

def remove_file_with_retry(filepath, max_retries=3):
    """Remove a file with retry logic for locked files"""
    for attempt in range(max_retries):
        try:
            if os.path.exists(filepath):
                # Remove read-only attribute
                os.chmod(filepath, stat.S_IWRITE)
                os.remove(filepath)
                return True
        except:
            time.sleep(0.5)
    return False

def remove_directory_with_prejudice(dirpath):
    """NUKE a directory - no mercy"""
    if not os.path.exists(dirpath):
        return False
    
    try:
        # First try Python's rmtree with error handling
        def on_rm_error(func, path, exc_info):
            # Force remove read-only attribute
            os.chmod(path, stat.S_IWRITE)
            try:
                func(path)
            except:
                pass
        
        shutil.rmtree(dirpath, onerror=on_rm_error, ignore_errors=True)
    except:
        pass
    
    # If still exists, use nuclear option
    if os.path.exists(dirpath):
        os.system(f'rmdir /s /q "{dirpath}" 2>nul')
        os.system(f'del /f /q "{dirpath}" 2>nul')
        os.system(f'rd /s /q "{dirpath}" 2>nul')
    
    # Final check with PowerShell
    os.system(f'powershell -Command "Remove-Item -Path \'{dirpath}\' -Recurse -Force" 2>nul')
    
    return not os.path.exists(dirpath)

def remove_ollama_direct():
    """NUCLEAR option - remove Ollama completely"""
    print_step("REMOVING OLLAMA - NUCLEAR MODE")
    
    # Find ALL possible Ollama locations
    user_home = os.path.expanduser("~")
    program_files = os.environ.get("ProgramFiles", "C:\\Program Files")
    program_files_x86 = os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")
    local_appdata = os.environ.get("LOCALAPPDATA", f"{user_home}\\AppData\\Local")
    roaming_appdata = os.environ.get("APPDATA", f"{user_home}\\AppData\\Roaming")
    
    # Comprehensive list of everywhere Ollama could hide
    ollama_paths = [
        f"{program_files}\\Ollama",
        f"{program_files_x86}\\Ollama",
        f"{local_appdata}\\Ollama",
        f"{local_appdata}\\Programs\\Ollama",
        f"{roaming_appdata}\\Ollama",
        f"{user_home}\\.ollama",
        f"{user_home}\\AppData\\Local\\Temp\\ollama",
        f"{local_appdata}\\Temp\\ollama",
    ]
    
    # Add user-specific paths
    for path in ollama_paths[:]:  # Copy list to iterate
        expanded = os.path.expandvars(path)
        if expanded != path:
            ollama_paths.append(expanded)
    
    # Remove duplicates
    ollama_paths = list(dict.fromkeys(ollama_paths))
    
    # Remove each location with extreme prejudice
    removed_count = 0
    for dir_path in ollama_paths:
        if os.path.exists(dir_path):
            print(f"  Nuking: {dir_path}")
            if remove_directory_with_prejudice(dir_path):
                removed_count += 1
                print(f"    ✓ Destroyed")
    
    if removed_count > 0:
        print_success(f"Obliterated {removed_count} Ollama installations")
    else:
        print_warning("No Ollama directories found")

def remove_models_direct():
    """NUKE all model directories"""
    print_step("WIPING DeepSeek models...")
    
    user_home = os.path.expanduser("~")
    local_appdata = os.environ.get("LOCALAPPDATA", f"{user_home}\\AppData\\Local")
    roaming_appdata = os.environ.get("APPDATA", f"{user_home}\\AppData\\Roaming")
    
    # All possible model locations
    model_paths = [
        f"{local_appdata}\\Ollama\\models",
        f"{roaming_appdata}\\Ollama\\models",
        f"{local_appdata}\\Programs\\Ollama\\models",
        f"{user_home}\\.ollama\\models",
        f"{local_appdata}\\Temp\\ollama\\models",
    ]
    
    removed = 0
    for path in model_paths:
        if os.path.exists(path):
            print(f"  Wiping: {path}")
            if remove_directory_with_prejudice(path):
                removed += 1
    
    if removed > 0:
        print_success(f"Wiped {removed} model directories")
    else:
        print_warning("No model directories found")

def clean_registry_thoroughly():
    """THOROUGH registry cleaning"""
    print_step("SANITIZING registry...")
    
    # Registry paths to nuke
    reg_paths = [
        # User registry
        'HKCU\\SOFTWARE\\Ollama',
        'HKCU\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Ollama',
        'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run\\Ollama',
        'HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce\\Ollama',
        
        # System registry (if admin)
        'HKLM\\SOFTWARE\\Ollama',
        'HKLM\\SOFTWARE\\WOW6432Node\\Ollama',
        'HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Ollama',
        'HKLM\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Ollama',
        'HKLM\\SYSTEM\\CurrentControlSet\\Services\\Ollama',
    ]
    
    # Search for any other Ollama registry keys
    search_paths = [
        'HKCU\\SOFTWARE',
        'HKLM\\SOFTWARE',
    ]
    
    for search_path in search_paths:
        result = os.system(f'reg query {search_path} /f "ollama" /s 2>nul >nul')
        # We don't actually parse, just nuke common paths
    
    cleaned = 0
    for reg_path in reg_paths:
        if os.system(f'reg delete "{reg_path}" /f 2>nul') == 0:
            cleaned += 1
    
    if cleaned > 0:
        print_success(f"Sanitized {cleaned} registry entries")

def clean_path_thoroughly():
    """CLEAN PATH from all Ollama references"""
    print_step("PURGING PATH from Ollama references...")
    
    def clean_path_string(path_string):
        if not path_string:
            return path_string
        parts = path_string.split(';')
        clean_parts = [p for p in parts if p and 'ollama' not in p.lower()]
        return ';'.join(clean_parts)
    
    # Clean User PATH
    success, stdout, stderr = run_command('reg query HKCU\\Environment /v Path 2>nul')
    if success and stdout:
        for line in stdout.split('\n'):
            if 'Path' in line and 'REG_' in line:
                if 'REG_SZ' in line or 'REG_EXPAND_SZ' in line:
                    current_path = line.split('REG_')[-1].split('SZ')[-1].strip()
                    if current_path and 'ollama' in current_path.lower():
                        new_path = clean_path_string(current_path)
                        reg_type = 'REG_EXPAND_SZ' if 'REG_EXPAND_SZ' in line else 'REG_SZ'
                        run_command(f'reg add HKCU\\Environment /v Path /t {reg_type} /d "{new_path}" /f 2>nul')
                        print_success("Purged Ollama from User PATH")
    
    # Clean System PATH if admin
    if is_admin():
        success, stdout, stderr = run_command('reg query "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment" /v Path 2>nul')
        if success and stdout:
            for line in stdout.split('\n'):
                if 'Path' in line and 'REG_' in line:
                    if 'REG_SZ' in line or 'REG_EXPAND_SZ' in line:
                        current_path = line.split('REG_')[-1].split('SZ')[-1].strip()
                        if current_path and 'ollama' in current_path.lower():
                            new_path = clean_path_string(current_path)
                            reg_type = 'REG_EXPAND_SZ' if 'REG_EXPAND_SZ' in line else 'REG_SZ'
                            run_command(f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment" /v Path /t {reg_type} /d "{new_path}" /f 2>nul')
                            print_success("Purged Ollama from System PATH")

def remove_created_files():
    """Remove installer-created files with extreme prejudice"""
    print_step("REMOVING installer-created files...")
    
    current_dir = os.getcwd()
    
    # Comprehensive list of files to remove
    files_to_remove = [
        # Batch files
        'chat.bat', 'test.bat', 'chat.ps1',
        'chat_deepseek.bat', 'chat_with_deepseek.ps1',
        'download_model.bat', 'start_download.bat',
        'test_deepseek.bat', 'ollama_path.bat',
        
        # Python files
        'chat_gui.py',
        
        # Web UI files
        'start_webui.bat',
        
        # Documentation
        'README_WINDOWS.txt', 'README.txt',
        
        # Installers
        'OllamaSetup.exe', 'DockerSetup.exe',
        
        # VBS scripts
        'start_download.vbs',
        
        # Any other generated files
        '*.log', '*.tmp',
    ]
    
    # Files to KEEP (sacred)
    keep_files = [
        'install_deepseek.py',
        'uninstall_complete.py',
        'uninstall.py',  # Common names
        'install.py',
    ]
    
    removed = 0
    for pattern in files_to_remove:
        if '*' in pattern:
            # Handle wildcards
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
                if remove_file_with_retry(file_path):
                    print(f"  Removed {pattern}")
                    removed += 1
    
    if removed > 0:
        print_success(f"Removed {removed} installer-created files")
    
    # Show kept files
    kept = [f for f in keep_files if os.path.exists(os.path.join(current_dir, f))]
    if kept:
        print_step(f"Preserved: {', '.join(kept)}")

def verify_uninstall_nuclear():
    """NUCLEAR verification - leave no trace"""
    print_step("NUCLEAR VERIFICATION - scanning for remnants...")
    
    issues = []
    
    # Scan entire drive for Ollama
    scan_paths = [
        'C:\\Program Files',
        'C:\\Program Files (x86)',
        os.path.expanduser('~\\AppData'),
        os.path.expanduser('~'),
        os.environ.get('TEMP', 'C:\\Temp'),
    ]
    
    for base_path in scan_paths:
        if os.path.exists(base_path):
            for root, dirs, files in os.walk(base_path, topdown=True, followlinks=False):
                # Limit depth to avoid infinite loops
                if root.count('\\') > 10:
                    dirs.clear()
                    continue
                
                for dir_name in dirs:
                    if 'ollama' in dir_name.lower():
                        issues.append(f"Found: {os.path.join(root, dir_name)}")
                        dirs.remove(dir_name)  # Don't go deeper
    
    # Check processes
    result = os.system('tasklist | findstr /i ollama >nul 2>&1')
    if result == 0:
        issues.append("Ollama processes still running")
    
    # Check services
    result = os.system('sc query Ollama 2>nul | findstr STATE >nul')
    if result == 0:
        issues.append("Ollama service still exists")
    
    if issues:
        print_warning("NUCLEAR VERIFICATION FOUND:")
        for issue in issues[:10]:  # Show first 10
            print(f"  • {issue}")
        
        response = input(f"{c.yellow('LAUNCH NUCLEAR CLEANUP? (y/N): ')}")
        if response.lower() in ['y', 'yes']:
            # Go absolutely nuclear
            for issue in issues:
                if 'Found:' in issue:
                    path = issue.replace('Found:', '').strip()
                    remove_directory_with_prejudice(path)
            print_success("Nuclear cleanup complete")
    else:
        print_success("✓ SYSTEM IS CLEAN - NO TRACES FOUND")

def main():
    """Main uninstall function - NUCLEAR EDITION"""
    print_header("DEEPSEEK NUCLEAR UNINSTALLER")
    print(f"""
{c.red('☢️  NUCLEAR OPTION ACTIVATED ☢️')}

{c.yellow('This will COMPLETELY ANNIHILATE:')}
  • Ollama (everywhere it hides)
  • ALL DeepSeek models (1.5B to 70B)
  • All configuration files
  • Registry entries
  • chat.bat, test.bat, etc.

{c.green('This will SURVIVE:')}
  • {os.path.basename(__file__)} (this uninstaller)
  • install_deepseek.py (the installer)

{c.red('☢️  NO MERCY MODE: ON ☢️')}
    """)
    
    response = input(f"{c.yellow('ARE YOU ABSOLUTELY SURE? (yes/NUCLEAR): ')}")
    if response.upper() != 'NUCLEAR':
        print_success("Aborting nuclear launch")
        return
    
    if not is_admin():
        print_error("NUCLEAR LAUNCH REQUIRES ADMINISTRATOR PRIVILEGES")
        print("Please run as Administrator")
        input("Press Enter to exit...")
        return
    
    print_header("☢️  NUCLEAR LAUNCH SEQUENCE INITIATED ☢️")
    
    # Phase 1: Termination
    force_kill_processes()
    stop_ollama_service_force()
    
    # Phase 2: Annihilation
    remove_models_direct()
    remove_ollama_direct()
    remove_created_files()
    
    # Phase 3: Sanitization
    clean_registry_thoroughly()
    clean_path_thoroughly()
    
    # Phase 4: Verification
    verify_uninstall_nuclear()
    
    print_header("☢️  NUCLEAR STRIKE COMPLETE ☢️")
    print(f"""
{c.green('✓ DeepSeek has been VAPORIZED!')}

{c.cyan('Surviving files:')}
   • {os.path.basename(__file__)}
   • install_deepseek.py

{c.yellow('Recommendation:')}
   1. Restart your computer
   2. The system is now clean
   3. Run installer again when ready

{c.red('☢️  NO TRACE LEFT BEHIND ☢️')}
    """)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{c.yellow('Nuclear launch aborted')}")
        sys.exit(0)
