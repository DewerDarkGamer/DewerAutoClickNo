"""
Window detection and manipulation utilities
"""

from typing import List, Tuple, Optional
import time
import sys
import os

from config import Config
from logger import Logger

# Only import Windows-specific modules when available
try:
    import ctypes
    import ctypes.wintypes
    WINDOWS_AVAILABLE = True
    
    # Windows API constants
    GW_HWNDNEXT = 2
    GWL_STYLE = -16
    WS_VISIBLE = 0x10000000
    WS_POPUP = 0x80000000
    WS_DLGFRAME = 0x00400000
    
except (ImportError, AttributeError):
    WINDOWS_AVAILABLE = False
    GW_HWNDNEXT = 2
    GWL_STYLE = -16
    WS_VISIBLE = 0x10000000
    WS_POPUP = 0x80000000
    WS_DLGFRAME = 0x00400000

class WindowDetector:
    def __init__(self):
        # Check if Windows is available
        if not WINDOWS_AVAILABLE:
            raise RuntimeError("This program only works on Windows")
            
        self.config = Config()
        self.logger = Logger()
        
        # Define Windows API functions
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Function prototypes
        self.EnumWindows = self.user32.EnumWindows
        self.EnumChildWindows = self.user32.EnumChildWindows
        self.GetWindowTextW = self.user32.GetWindowTextW
        self.GetClassNameW = self.user32.GetClassNameW
        self.GetWindowRect = self.user32.GetWindowRect
        self.IsWindowVisible = self.user32.IsWindowVisible
        self.GetWindowLongW = self.user32.GetWindowLongW
        self.GetWindowThreadProcessId = self.user32.GetWindowThreadProcessId
    
    def find_popup_windows(self) -> List[Tuple[int, str]]:
        """
        Find all popup/notification windows
        Returns list of (hwnd, window_title) tuples
        """
        if not WINDOWS_AVAILABLE:
            return []
            
        popup_windows = []
        
        def enum_windows_proc(hwnd, lparam):
            try:
                if self._is_popup_window(hwnd):
                    window_title = self._get_window_text(hwnd)
                    if window_title:  # Only include windows with titles
                        popup_windows.append((hwnd, window_title))
                        self.logger.debug(f"Found popup candidate: {window_title} (HWND: {hwnd})")
            except Exception as e:
                self.logger.debug(f"Error processing window {hwnd}: {e}")
            return True  # Continue enumeration
        
        # Convert Python function to Windows callback
        enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)(enum_windows_proc)
        
        try:
            self.EnumWindows(enum_proc, 0)
        except Exception as e:
            self.logger.error(f"Error enumerating windows: {e}")
        
        return popup_windows
    
    def _is_popup_window(self, hwnd: int) -> bool:
        """
        Check if a window is likely a popup/notification window
        """
        if not WINDOWS_AVAILABLE:
            return False
            
        try:
            # Must be visible
            if not self.IsWindowVisible(hwnd):
                return False
            
            # Check window style
            style = self.GetWindowLongW(hwnd, GWL_STYLE)
            if not (style & WS_VISIBLE):
                return False
            
            # Check if it's a dialog or popup
            is_dialog = (style & WS_DLGFRAME) != 0
            is_popup = (style & WS_POPUP) != 0
            
            # Get window class
            class_name = self._get_window_class(hwnd)
            is_popup_class = any(popup_class.lower() in class_name.lower() 
                               for popup_class in self.config.popup_classes)
            
            # Get window title and check for popup keywords
            window_title = self._get_window_text(hwnd)
            has_popup_keywords = any(keyword.lower() in window_title.lower() 
                                   for keyword in self.config.popup_title_keywords)
            
            # Check window size
            rect = ctypes.wintypes.RECT()
            if self.GetWindowRect(hwnd, ctypes.byref(rect)):
                width = rect.right - rect.left
                height = rect.bottom - rect.top
                
                min_w, min_h = self.config.min_popup_size
                max_w, max_h = self.config.max_popup_size
                
                size_ok = (min_w <= width <= max_w) and (min_h <= height <= max_h)
            else:
                size_ok = True  # If we can't get size, assume it's ok
            
            # Check if window belongs to ignored process
            if self._is_ignored_process(hwnd):
                return False
            
            # A window is considered a popup if it meets any of these criteria:
            # 1. It's a dialog with popup keywords in title
            # 2. It has a popup class name
            # 3. It's a popup window with reasonable size
            result = size_ok and (
                (is_dialog and has_popup_keywords) or
                is_popup_class or
                (is_popup and has_popup_keywords)
            )
            
            if result:
                self.logger.debug(f"Popup detected - Title: '{window_title}', Class: '{class_name}', "
                                f"Dialog: {is_dialog}, Popup: {is_popup}, Size OK: {size_ok}")
            
            return result
            
        except Exception as e:
            self.logger.debug(f"Error checking if window {hwnd} is popup: {e}")
            return False
    
    def _get_window_text(self, hwnd: int) -> str:
        """Get window title text"""
        if not WINDOWS_AVAILABLE:
            return ""
        try:
            length = self.user32.GetWindowTextLengthW(hwnd) + 1
            buffer = ctypes.create_unicode_buffer(length)
            self.GetWindowTextW(hwnd, buffer, length)
            return buffer.value
        except Exception:
            return ""
    
    def _get_window_class(self, hwnd: int) -> str:
        """Get window class name"""
        if not WINDOWS_AVAILABLE:
            return ""
        try:
            buffer = ctypes.create_unicode_buffer(256)
            self.GetClassNameW(hwnd, buffer, 256)
            return buffer.value
        except Exception:
            return ""
    
    def _is_ignored_process(self, hwnd: int) -> bool:
        """Check if window belongs to an ignored process"""
        if not WINDOWS_AVAILABLE:
            return False
        try:
            process_id = ctypes.wintypes.DWORD()
            self.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
            
            # Get process name
            hProcess = self.kernel32.OpenProcess(0x1000, False, process_id.value)  # PROCESS_QUERY_LIMITED_INFORMATION
            if hProcess:
                try:
                    buffer = ctypes.create_unicode_buffer(260)
                    size = ctypes.wintypes.DWORD(260)
                    if self.kernel32.QueryFullProcessImageNameW(hProcess, 0, buffer, ctypes.byref(size)):
                        process_path = buffer.value
                        process_name = process_path.split('\\')[-1].lower()
                        return process_name in [p.lower() for p in self.config.ignored_processes]
                finally:
                    self.kernel32.CloseHandle(hProcess)
        except Exception as e:
            self.logger.debug(f"Error checking process for window {hwnd}: {e}")
        
        return False
    
    def find_button_by_text(self, parent_hwnd: int, target_texts: List[str]) -> Optional[int]:
        """
        Find a button with specific text within a window
        Returns button HWND if found, None otherwise
        """
        if not WINDOWS_AVAILABLE:
            return None
            
        found_button = None
        
        def enum_child_proc(hwnd, lparam):
            nonlocal found_button
            try:
                # Check if it's a button
                class_name = self._get_window_class(hwnd)
                if 'button' in class_name.lower():
                    button_text = self._get_window_text(hwnd)
                    
                    # Check if button text matches any target text
                    for target in target_texts:
                        if target.lower() in button_text.lower() or button_text.lower() in target.lower():
                            self.logger.debug(f"Found matching button: '{button_text}' (HWND: {hwnd})")
                            found_button = hwnd
                            return False  # Stop enumeration
                            
            except Exception as e:
                self.logger.debug(f"Error processing child window {hwnd}: {e}")
            return True  # Continue enumeration
        
        # Convert Python function to Windows callback
        enum_proc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.wintypes.HWND, ctypes.wintypes.LPARAM)(enum_child_proc)
        
        try:
            self.EnumChildWindows(parent_hwnd, enum_proc, 0)
        except Exception as e:
            self.logger.error(f"Error enumerating child windows: {e}")
        
        return found_button