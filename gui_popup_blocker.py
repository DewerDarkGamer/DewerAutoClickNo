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
        Handle a detected popup window with retry mechanism
        Returns True if a button was successfully clicked
        """
        if not WINDOWS_AVAILABLE:
            return False
            
        try:
            max_retries = 3  # คลิกซ้ำสูงสุด 3 ครั้ง
            
            for attempt in range(max_retries):
                self.logger.debug(f"Attempt {attempt + 1} to handle popup '{window_title}'")
                
                # First, try to find and click standard dialog buttons
                if self._click_standard_dialog_button_with_retry(hwnd):
                    self.logger.info(f"Clicked standard dialog button in '{window_title}' (attempt {attempt + 1})")
                    
                    # ตรวจสอบว่าปุ่มหายไปหรือยัง
                    time.sleep(0.5)  # รอให้หน้าต่างประมวลผล
                    if not self._popup_still_exists(hwnd):
                        return True
                    else:
                        self.logger.debug(f"Popup still exists after standard click, retrying...")
                        continue
                
                # If standard approach fails, try to find buttons by text
                button_hwnd = self.detector.find_button_by_text(hwnd, self.config.target_buttons)
                if button_hwnd:
                    if self._click_button_enhanced(button_hwnd, window_title, attempt + 1):
                        self.logger.info(f"Clicked 'No' button in '{window_title}' (attempt {attempt + 1})")
                        
                        # ตรวจสอบว่าปุ่มหายไปหรือยัง
                        time.sleep(0.5)  # รอให้หน้าต่างประมวลผล
                        if not self._popup_still_exists(hwnd):
                            return True
                        else:
                            # ตรวจสอบว่าปุ่ม "no" ยังอยู่หรือไม่
                            button_still_exists = self.detector.find_button_by_text(hwnd, self.config.target_buttons)
                            if not button_still_exists:
                                self.logger.info(f"No button disappeared after click")
                                return True
                            else:
                                self.logger.debug(f"Button still exists, retrying...")
                                continue
                
                # รอก่อนลองครั้งต่อไป
                if attempt < max_retries - 1:
                    time.sleep(0.3)
            
            self.logger.warning(f"Failed to handle popup '{window_title}' after {max_retries} attempts")
            return False
            
        except Exception as e:
            self.logger.error(f"Error handling popup '{window_title}': {e}")
            self.stats['errors'] += 1
            return False
    
    def _click_button(self, button_hwnd: int) -> bool:
        """
        Legacy click function for backward compatibility
        """
        return self._click_button_enhanced(button_hwnd, "unknown", 1)
    
    def _click_button_enhanced(self, button_hwnd: int, window_title: str, attempt: int) -> bool:
        """
        Enhanced button clicking with multiple methods and better error handling
        Returns True if successful
        """
        if not WINDOWS_AVAILABLE:
            return False
            
        try:
            self.logger.debug(f"Attempting to click button (method enhanced, attempt {attempt})")
            
            # Method 1: Send BM_CLICK message
            try:
                result = ctypes.windll.user32.SendMessageW(button_hwnd, BM_CLICK, 0, 0)
                time.sleep(0.2)  # รอให้ click ประมวลผล
                if result is not None:  # ไม่ใช่ result == 0 เพราะอาจส่งคืนค่าอื่น
                    self.logger.debug(f"BM_CLICK sent successfully")
                    return True
            except Exception as e:
                self.logger.debug(f"BM_CLICK failed: {e}")
            
            # Method 2: Enhanced mouse click simulation
            try:
                rect = ctypes.wintypes.RECT()
                if ctypes.windll.user32.GetWindowRect(button_hwnd, ctypes.byref(rect)):
                    center_x = (rect.left + rect.right) // 2
                    center_y = (rect.top + rect.bottom) // 2
                    
                    self.logger.debug(f"Clicking at position ({center_x}, {center_y})")
                    
                    # เก็บตำแหน่งเมาส์เดิม
                    old_pos = ctypes.wintypes.POINT()
                    ctypes.windll.user32.GetCursorPos(ctypes.byref(old_pos))
                    
                    # Set cursor position
                    ctypes.windll.user32.SetCursorPos(center_x, center_y)
                    time.sleep(0.1)
                    
                    # Multiple click attempts
                    for i in range(2):  # คลิก 2 ครั้งเผื่อครั้งแรกไม่ติด
                        # Left mouse down
                        ctypes.windll.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
                        time.sleep(0.05)
                        # Left mouse up
                        ctypes.windll.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
                        time.sleep(0.1)
                    
                    # คืนตำแหน่งเมาส์เดิม
                    ctypes.windll.user32.SetCursorPos(old_pos.x, old_pos.y)
                    
                    self.logger.debug(f"Mouse click completed")
                    return True
            except Exception as e:
                self.logger.debug(f"Mouse click failed: {e}")
            
            # Method 3: Send WM_LBUTTONDOWN/UP messages directly to button
            try:
                ctypes.windll.user32.SendMessageW(button_hwnd, WM_LBUTTONDOWN, 1, 0)
                time.sleep(0.05)
                ctypes.windll.user32.SendMessageW(button_hwnd, WM_LBUTTONUP, 0, 0)
                time.sleep(0.1)
                self.logger.debug(f"Direct button message sent")
                return True
            except Exception as e:
                self.logger.debug(f"Direct button message failed: {e}")
            
            # Method 4: Try PostMessage instead of SendMessage
            try:
                ctypes.windll.user32.PostMessageW(button_hwnd, BM_CLICK, 0, 0)
                time.sleep(0.2)
                self.logger.debug(f"PostMessage BM_CLICK sent")
                return True
            except Exception as e:
                self.logger.debug(f"PostMessage failed: {e}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error in enhanced button click: {e}")
            return False
    
    def _click_standard_dialog_button_with_retry(self, hwnd: int) -> bool:
        """
        Try to click standard dialog buttons with retry
        Returns True if successful
        """
        if not WINDOWS_AVAILABLE:
            return False
            
        try:
            # Try IDNO multiple times with different methods
            for i in range(2):
                try:
                    # Method 1: SendMessage
                    result = ctypes.windll.user32.SendMessageW(hwnd, WM_COMMAND, IDNO, 0)
                    time.sleep(0.2)
                    if result is not None:
                        return True
                except Exception:
                    pass
                
                try:
                    # Method 2: PostMessage
                    ctypes.windll.user32.PostMessageW(hwnd, WM_COMMAND, IDNO, 0)
                    time.sleep(0.2)
                    return True
                except Exception:
                    pass
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Standard dialog approach failed: {e}")
            return False
    
    def _popup_still_exists(self, hwnd: int) -> bool:
        """
        Check if popup window still exists and is visible
        """
        if not WINDOWS_AVAILABLE:
            return False
            
        try:
            # ตรวจสอบว่าหน้าต่างยังมองเห็นได้หรือไม่
            return bool(ctypes.windll.user32.IsWindowVisible(hwnd) and 
                       ctypes.windll.user32.IsWindow(hwnd))
        except Exception:
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
