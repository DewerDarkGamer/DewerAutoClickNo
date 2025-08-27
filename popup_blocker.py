#!/usr/bin/env python3
"""
Popup Blocker - Automatically clicks 'No' on popup notifications
Uses built-in Windows capabilities only - no external dependencies required
"""

import time
import sys
import os
from typing import List, Tuple, Optional
import threading
import signal

# Only import Windows-specific modules when available
try:
    import ctypes
    import ctypes.wintypes
    WINDOWS_AVAILABLE = True
except (ImportError, AttributeError):
    WINDOWS_AVAILABLE = False

from config import Config
from logger import Logger

if WINDOWS_AVAILABLE:
    from window_detector import WindowDetector

# Windows API constants
WM_COMMAND = 0x0111
BM_CLICK = 0x00F5
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
IDNO = 7
IDCANCEL = 2

class PopupBlocker:
    def __init__(self):
        # Check if Windows is available
        if not WINDOWS_AVAILABLE:
            raise RuntimeError("This program only works on Windows")
            
        self.config = Config()
        self.logger = Logger()
        self.detector = WindowDetector()
        self.running = False
        self.stats = {
            'popups_detected': 0,
            'buttons_clicked': 0,
            'errors': 0
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info("Shutdown signal received. Stopping popup blocker...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start the popup blocker service"""
        if not WINDOWS_AVAILABLE:
            self.logger.error("This program only works on Windows")
            return
            
        self.logger.info("Starting Popup Blocker...")
        self.logger.info(f"Check interval: {self.config.check_interval}s")
        self.logger.info(f"Target button texts: {self.config.target_buttons}")
        
        self.running = True
        
        try:
            while self.running:
                self._check_for_popups()
                time.sleep(self.config.check_interval)
        except KeyboardInterrupt:
            self.logger.info("Keyboard interrupt received")
        except Exception as e:
            self.logger.error(f"Unexpected error in main loop: {e}")
            self.stats['errors'] += 1
        finally:
            self.stop()
    
    def stop(self):
        """Stop the popup blocker service"""
        self.running = False
        self._print_stats()
        self.logger.info("Popup Blocker stopped")
    
    def _check_for_popups(self):
        """Check for popup windows and handle them"""
        if not WINDOWS_AVAILABLE:
            return
            
        try:
            popup_windows = self.detector.find_popup_windows()
            
            for hwnd, window_title in popup_windows:
                self.stats['popups_detected'] += 1
                self.logger.info(f"Detected popup: '{window_title}' (HWND: {hwnd})")
                
                if self._handle_popup(hwnd, window_title):
                    self.stats['buttons_clicked'] += 1
                    
        except Exception as e:
            self.logger.error(f"Error checking for popups: {e}")
            self.stats['errors'] += 1
    
    def _handle_popup(self, hwnd: int, window_title: str) -> bool:
        """
        Handle a detected popup window
        Returns True if a button was successfully clicked
        """
        if not WINDOWS_AVAILABLE:
            return False
            
        try:
            # First, try to find and click standard dialog buttons
            if self._click_standard_dialog_button(hwnd):
                self.logger.info(f"Clicked standard dialog button in '{window_title}'")
                return True
            
            # If standard approach fails, try to find buttons by text
            button_hwnd = self.detector.find_button_by_text(hwnd, self.config.target_buttons)
            if button_hwnd:
                if self._click_button(button_hwnd):
                    self.logger.info(f"Clicked 'No' button in '{window_title}'")
                    return True
            
            self.logger.warning(f"No 'No' button found in popup '{window_title}'")
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling popup '{window_title}': {e}")
            self.stats['errors'] += 1
            return False
    
    def _click_standard_dialog_button(self, hwnd: int) -> bool:
        """
        Try to click standard dialog buttons (IDNO, IDCANCEL)
        Returns True if successful
        """
        if not WINDOWS_AVAILABLE:
            return False
            
        try:
            # Try IDNO first (standard 'No' button)
            result = ctypes.windll.user32.SendMessageW(hwnd, WM_COMMAND, IDNO, 0)
            if result == 0:  # Success
                return True
            
            # Don't try IDCANCEL since we only want "No" buttons, not "Cancel"
            return False
            
        except Exception as e:
            self.logger.debug(f"Standard dialog approach failed: {e}")
            return False
    
    def _click_button(self, button_hwnd: int) -> bool:
        """
        Click a button using Windows API
        Returns True if successful
        """
        if not WINDOWS_AVAILABLE:
            return False
            
        try:
            # Method 1: Send BM_CLICK message
            result = ctypes.windll.user32.SendMessageW(button_hwnd, BM_CLICK, 0, 0)
            if result == 0:
                return True
            
            # Method 2: Simulate mouse click
            rect = ctypes.wintypes.RECT()
            if ctypes.windll.user32.GetWindowRect(button_hwnd, ctypes.byref(rect)):
                center_x = (rect.left + rect.right) // 2
                center_y = (rect.top + rect.bottom) // 2
                
                # Set cursor position and click
                ctypes.windll.user32.SetCursorPos(center_x, center_y)
                time.sleep(0.1)  # Small delay
                
                ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
                time.sleep(0.05)
                ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
                
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error clicking button: {e}")
            return False
    
    def _print_stats(self):
        """Print statistics about the session"""
        self.logger.info("=== Session Statistics ===")
        self.logger.info(f"Popups detected: {self.stats['popups_detected']}")
        self.logger.info(f"Buttons clicked: {self.stats['buttons_clicked']}")
        self.logger.info(f"Errors encountered: {self.stats['errors']}")
        
        if self.stats['popups_detected'] > 0:
            success_rate = (self.stats['buttons_clicked'] / self.stats['popups_detected']) * 100
            self.logger.info(f"Success rate: {success_rate:.1f}%")

def main():
    """Main entry point"""
    if not WINDOWS_AVAILABLE:
        print("Error: This program only works on Windows")
        print("ข้อผิดพลาด: โปรแกรมนี้ทำงานได้เฉพาะบน Windows เท่านั้น")
        sys.exit(1)
    
    print("Popup Blocker - Automatic 'No' Button Clicker")
    print("=" * 50)
    print("Press Ctrl+C to stop")
    print()
    
    blocker = PopupBlocker()
    
    try:
        blocker.start()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()