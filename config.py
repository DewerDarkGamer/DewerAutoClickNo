"""
Configuration settings for the Popup Blocker
"""

import os

class Config:
    def __init__(self):
        # How often to check for popups (in seconds)
        self.check_interval = float(os.getenv('CHECK_INTERVAL', '2.0'))
        
        # Button texts to look for - ONLY "No" buttons (no Cancel)
        self.target_buttons = [
            'No',
            'no', 
            'NO',
            'ไม่',          # Thai 'No'
            'ไม่ต้องการ',   # Thai 'Don't want'
        ]
        
        # Window class names that are commonly used for popups/dialogs
        self.popup_classes = [
            '#32770',      # Standard dialog box
            'Dialog',
            'TDialog',
            'PopupWindow',
            'AlertWindow',
            'MessageBox',
            'ConfirmDialog',
            'NotificationWindow',
        ]
        
        # Window titles that suggest popup/notification windows
        self.popup_title_keywords = [
            'notification',
            'alert',
            'warning',
            'confirm',
            'dialog',
            'popup',
            'message',
            'แจ้งเตือน',    # Thai 'notification'
            'ยืนยัน',       # Thai 'confirm'
            'คำเตือน',      # Thai 'warning'
        ]
        
        # Minimum window size to consider (width, height)
        # This helps filter out very small windows that aren't real popups
        self.min_popup_size = (100, 50)
        
        # Maximum window size to consider (width, height)
        # This helps filter out full-screen applications
        self.max_popup_size = (800, 600)
        
        # Enable debug logging
        self.debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
        
        # Log file path
        self.log_file = os.getenv('LOG_FILE', 'popup_blocker.log')
        
        # Maximum number of log entries to keep in memory
        self.max_log_entries = int(os.getenv('MAX_LOG_ENTRIES', '1000'))
        
        # Delay before clicking button (in seconds)
        # This prevents clicking too quickly on legitimate dialogs
        self.click_delay = float(os.getenv('CLICK_DELAY', '0.5'))
        
        # Process names to ignore (don't click their popups)
        self.ignored_processes = [
            'explorer.exe',
            'winlogon.exe',
            'csrss.exe',
            'dwm.exe',
            'taskmgr.exe',
        ]
