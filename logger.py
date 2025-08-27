"""
Logging utility for the Popup Blocker
"""

import time
import os
from datetime import datetime
from typing import List
from config import Config

class Logger:
    def __init__(self):
        self.config = Config()
        self.log_entries: List[str] = []
        self.log_file_path = self.config.log_file
        
        # Create log file if it doesn't exist
        self._ensure_log_file()
    
    def _ensure_log_file(self):
        """Ensure log file exists and is writable"""
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(f"\n=== Popup Blocker Started at {datetime.now()} ===\n")
        except Exception as e:
            print(f"Warning: Cannot write to log file {self.log_file_path}: {e}")
            self.log_file_path = None
    
    def _log(self, level: str, message: str):
        """Internal logging method"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        # Print to console
        print(log_entry)
        
        # Add to memory log
        self.log_entries.append(log_entry)
        
        # Trim log entries if too many
        if len(self.log_entries) > self.config.max_log_entries:
            self.log_entries = self.log_entries[-self.config.max_log_entries:]
        
        # Write to file if available
        if self.log_file_path:
            try:
                with open(self.log_file_path, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
                    f.flush()
            except Exception as e:
                print(f"Warning: Cannot write to log file: {e}")
    
    def info(self, message: str):
        """Log info message"""
        self._log("INFO", message)
    
    def warning(self, message: str):
        """Log warning message"""
        self._log("WARN", message)
    
    def error(self, message: str):
        """Log error message"""
        self._log("ERROR", message)
    
    def debug(self, message: str):
        """Log debug message (only if debug mode is enabled)"""
        if self.config.debug_mode:
            self._log("DEBUG", message)
    
    def get_recent_logs(self, count: int = 50) -> List[str]:
        """Get recent log entries"""
        return self.log_entries[-count:] if count > 0 else self.log_entries
    
    def clear_logs(self):
        """Clear in-memory log entries"""
        self.log_entries.clear()
        self.info("Log entries cleared")
