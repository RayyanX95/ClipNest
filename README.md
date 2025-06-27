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

### DMG Packaging Command

To create a macOS disk image (DMG) for easy distribution, use the following `create-dmg` command:

```bash
create-dmg \
   --volname "ClipNest" \
   --window-pos 200 120 \
   --window-size 500 300 \
   --icon-size 100 \
   --icon ClipNest.app 125 150 \
   --app-drop-link 375 150 \
   dist/ClipNest.dmg \
   dist/ClipNest.app
```

- `--volname`: Sets the name of the mounted DMG volume.
- `--window-pos` and `--window-size`: Define the position and size of the DMG window when opened.
- `--icon-size`: Sets the size of the application icon in the DMG window.
- `--icon`: Places the app icon at the specified coordinates.
- `--app-drop-link`: Adds a shortcut to the Applications folder for easy installation.
- The last two arguments specify the output DMG file and the app bundle to include.

After running this command, you'll have a `ClipNest.dmg` file in the `dist` directory, which users can open and drag the app into their Applications folder.

### DMG Packaging Commands for Apple Silicon and Intel Builds

Below are example commands to create DMG installers for both Apple Silicon (arm64) and Intel (x86_64) versions of the app. This allows you to distribute native builds optimized for each architecture.

- **Apple Silicon (arm64):**

  ```bash
  create-dmg --volname "ClipNest (Apple Silicon)" --window-pos 200 120 --window-size 500 300 --icon-size 100 --icon ClipNest-arm64.app 125 150 --app-drop-link 375 150 dist/ClipNest-arm64.dmg dist/ClipNest-arm64.app
  ```

- **Intel (x86_64):**
  ```bash
  create-dmg --volname "ClipNest (Intel)" --window-pos 200 120 --window-size 500 300 --icon-size 100 --icon ClipNest-x86_64.app 125 150 --app-drop-link 375 150 dist/ClipNest-x86_64.dmg dist/ClipNest-x86_64.app
  ```

Each command generates a `.dmg` file in the `dist` directory, ready for distribution to users on the corresponding Mac architecture.
