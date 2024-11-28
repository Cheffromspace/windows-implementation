import subprocess
import platform
import os
from typing import Optional, Dict, Any

class CommandRouter:
    def __init__(self):
        self.is_windows = platform.system().lower() == "windows"
        
    def run_bash(self, command: str) -> Dict[str, Any]:
        """Run a command in WSL bash"""
        try:
            if self.is_windows:
                # When running on Windows, prefix with wsl command
                full_command = f"wsl bash -c '{command}'"
                result = subprocess.run(full_command, shell=True, text=True, capture_output=True)
            else:
                # Direct bash execution for when running in WSL
                result = subprocess.run(command, shell=True, text=True, capture_output=True)
            
            return {
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "return_code": -1
            }

    def run_powershell(self, command: str) -> Dict[str, Any]:
        """Run a command in PowerShell"""
        try:
            if not self.is_windows:
                raise Exception("PowerShell commands can only be run on Windows")
            
            full_command = f"powershell.exe -Command {command}"
            result = subprocess.run(full_command, shell=True, text=True, capture_output=True)
            
            return {
                "output": result.stdout,
                "error": result.stderr,
                "return_code": result.returncode
            }
        except Exception as e:
            return {
                "output": "",
                "error": str(e),
                "return_code": -1
            }