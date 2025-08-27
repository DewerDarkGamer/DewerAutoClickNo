# Overview

This is a Windows desktop automation tool that automatically detects popup notifications and clicks "No" buttons using built-in Windows APIs. The application comes in two versions:
1. **Console Version** (`popup_blocker.py`) - Command-line background service
2. **GUI Version** (`gui_popup_blocker.py`) - User-friendly interface with start/stop controls

Both versions support English and Thai languages and provide comprehensive logging and statistics tracking. The GUI version also includes screen lock prevention functionality.

# User Preferences

- Preferred communication style: Simple, everyday language
- Only click "No" buttons, never "Cancel" buttons
- Requires GUI with start/stop controls
- Needs screen lock prevention (computer locks every 5 minutes)

# System Architecture

## Core Components
The application follows a modular architecture with clear separation of concerns:

- **PopupBlocker**: Main orchestration class that coordinates the detection and clicking operations
- **WindowDetector**: Handles Windows API calls for window enumeration and popup identification  
- **Logger**: Centralized logging system with both console and file output
- **Config**: Configuration management using environment variables
- **PopupBlockerGUI**: GUI interface with tkinter for user-friendly control
- **MouseMover**: Prevents screen lock by moving mouse every 4 minutes

## Design Patterns
- **Strategy Pattern**: Used for different popup detection methods and button identification
- **Observer Pattern**: Implemented through signal handlers for graceful shutdown
- **Singleton-like Configuration**: Single config instance shared across components

## Windows API Integration
The application leverages native Windows APIs through ctypes:
- `EnumWindows` and `EnumChildWindows` for window discovery
- Window style checking (`WS_VISIBLE`, `WS_POPUP`, `WS_DLGFRAME`) for popup identification
- `SendMessage` with `BM_CLICK` for automated button clicking
- Process and thread ID checking for security filtering

## Multi-language Support
Built-in internationalization supporting:
- English button texts (No only, Cancel excluded per user preference)
- Thai button texts (ไม่, ไม่ต้องการ only)
- Extensible button text configuration system
- GUI interface with Thai language support

## Safety Mechanisms
- Process filtering to avoid clicking on critical system dialogs
- Configurable delays to prevent race conditions
- Window class validation to target only legitimate popup windows
- Graceful error handling with comprehensive logging

# External Dependencies

## System Requirements
- Windows operating system (uses Windows-specific APIs)
- Python 3.x runtime environment
- Built-in Windows libraries (user32.dll, kernel32.dll)

## No External Libraries
The application is specifically designed to use only built-in Python modules and Windows APIs:
- `ctypes` for Windows API access
- `threading` for background operation
- `signal` for shutdown handling
- `tkinter` for GUI interface (included with Python)
- Standard library modules for logging and configuration

## Configuration Sources
- Environment variables for runtime configuration
- Local file system for log output
- Windows registry and system APIs for window detection