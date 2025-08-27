# Popup Blocker - Automatic 'No' Button Clicker

A Windows desktop automation script that automatically detects popup notifications and clicks "No" buttons using built-in Windows capabilities. No external software installation required.

## Features

- 🚫 Automatically clicks "No" on popup dialogs
- 🔍 Detects various popup window patterns
- 🌐 Supports both English and Thai button text
- 📊 Provides logging and statistics
- ⚡ Uses only built-in Windows APIs (no external dependencies)
- 🛡️ Safe operation with process filtering
- ⚙️ Configurable settings via environment variables

## Quick Start

### Method 1: Using Batch File (Recommended)
1. Double-click `run.bat`
2. The script will start automatically
3. Press `Ctrl+C` to stop

### Method 2: Using Command Line
1. Open Command Prompt
2. Navigate to the script directory
3. Run: `python popup_blocker.py`

## Configuration

You can customize the behavior using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `CHECK_INTERVAL` | How often to check for popups (seconds) | `2.0` |
| `DEBUG` | Enable debug logging (`true`/`false`) | `false` |
| `LOG_FILE` | Path to log file | `popup_blocker.log` |
| `CLICK_DELAY` | Delay before clicking button (seconds) | `0.5` |

### Example with custom settings:
```batch
set CHECK_INTERVAL=1.5
set DEBUG=true
python popup_blocker.py
