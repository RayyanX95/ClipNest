#!/usr/bin/env python3
"""
Advanced Clipboard Manager for macOS - Simple Version
Main application entry point and orchestration.
"""

import signal
import sys

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication

from clipboard_monitor import ClipboardMonitor
from database import ClipboardDatabase
from ui import ClipboardManagerUI


class ClipboardManagerApp:
    """Main application class that coordinates all components."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("Clipboard Manager")
        self.app.setQuitOnLastWindowClosed(False)  # Keep running in background

        # Apply dark theme stylesheet
        self.app.setStyleSheet(
            """
            QWidget { background-color: #232629; color: #f0f0f0; }
            QLineEdit, QTextEdit { background-color: #2b2b2b; color: #f0f0f0; border: 1px solid #444; }
            QListWidget, QListWidgetItem { background-color: #232629; color: #f0f0f0; }
            QPushButton { background-color: #444; color: #f0f0f0; border: 1px solid #666; padding: 4px 12px; border-radius: 4px; }
            QPushButton:hover { background-color: #555; }
            QLabel { color: #f0f0f0; }
            QMenu { background-color: #232629; color: #f0f0f0; }
            QMenu::item:selected { background-color: #444; }
            QStatusBar { background: #232629; color: #f0f0f0; }
        """
        )

        # Initialize components
        self.database = ClipboardDatabase()
        self.monitor = ClipboardMonitor(self.database)
        self.ui = ClipboardManagerUI(self.database)

        # Connect signals
        self.monitor.new_item_signal.connect(self.ui.refresh_history)

        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Timer to handle Ctrl+C in Qt event loop
        self.timer = QTimer()
        self.timer.start(500)
        self.timer.timeout.connect(lambda: None)

    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}, shutting down...")
        self.shutdown()

    def run(self):
        """Start the application."""
        print("Starting Clipboard Manager...")

        # Start clipboard monitoring
        self.monitor.start_monitoring()

        # Show the UI (initially hidden, accessed via menubar)
        self.ui.setup_menubar()

        # Run the application
        return self.app.exec()

    def shutdown(self):
        """Clean shutdown of all components."""
        print("Shutting down Clipboard Manager...")
        self.monitor.stop_monitoring()
        self.database.close()
        self.app.quit()


def main():
    """Main entry point."""
    app = ClipboardManagerApp()
    try:
        sys.exit(app.run())
    except KeyboardInterrupt:
        app.shutdown()
    except Exception as e:
        print(f"Error: {e}")
        app.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    main()
