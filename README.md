# Advanced Clipboard Manager for macOS - Simple Version

A simple yet functional clipboard manager for macOS that monitors clipboard changes and provides a searchable history with favorites.

## Features (Simple Version)

- **Clipboard Monitoring**: Automatically captures text copied to clipboard
- **Persistent History**: Stores up to 200 items in SQLite database
- **Search Functionality**: Quickly find items in clipboard history
- **Favorites**: Mark important items as favorites (starred)
- **System Tray Integration**: Runs in background with menubar icon
- **Clean UI**: Native-looking interface with PyQt6

## Setup Instructions

### Prerequisites

- macOS 10.14 or later
- Python 3.8 or later
- pip package manager

### Installation Steps

1. **Clone or download the project files**

   ```bash
   mkdir clipboard_manager
   cd clipboard_manager
   # Place all the Python files in this directory
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

1. **Start the application**

   ```bash
   python main.py
   ```

2. **The application will:**

   - Start monitoring your clipboard
   - Show a small icon in the system tray/menubar
   - Begin storing clipboard history in `~/.clipboard_manager/clipboard_history.db`

3. **Access the interface:**
   - Click the system tray icon to show the main window

### Build Command

To package the application as a standalone macOS app, use the following PyInstaller command:

```bash
venv/bin/pyinstaller --windowed --noconfirm --name "ClipNest" --icon icon.icns --add-data "clip_app_icon_light.png:." --add-data "clip_app_icon_dark.png:." main.py
```

- `--windowed`: Runs the app without opening a terminal window.
- `--noconfirm`: Overwrites any existing build files without prompting.
- `--name`: Sets the name of the generated application.
- `--icon`: Specifies the application icon (`.icns` format for macOS).
- `--add-data`: Includes additional resource files (icons) in the build.
- `main.py`: The entry point of your application.

After running this command, the packaged app will be available in the `dist/ClipboardManager` directory, ready to run on macOS without requiring Python to be installed.
