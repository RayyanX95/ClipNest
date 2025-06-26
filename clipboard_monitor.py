"""
Clipboard monitoring module for detecting and processing clipboard changes for ClipNest.
"""

import threading
import time
from datetime import datetime

import pyperclip
from PyQt6.QtCore import QObject, pyqtSignal


class ClipNestMonitor(QObject):
    """Monitor system clipboard for changes and store new items for ClipNest."""

    # Signal emitted when a new item is added to clipboard
    new_item_signal = pyqtSignal()

    def __init__(self, database):
        super().__init__()
        self.database = database
        self.monitoring = False
        self.monitor_thread = None
        self.last_clipboard_content = ""

    def start_monitoring(self):
        """Start monitoring clipboard changes in a separate thread."""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("Clipboard monitoring started")

    def stop_monitoring(self):
        """Stop clipboard monitoring."""
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        print("Clipboard monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop that runs in a separate thread."""
        # Get initial clipboard content
        try:
            self.last_clipboard_content = pyperclip.paste()
        except Exception as e:
            print(f"Error getting initial clipboard content: {e}")
            self.last_clipboard_content = ""

        while self.monitoring:
            try:
                current_content = pyperclip.paste()

                # Check if clipboard content has changed
                if current_content != self.last_clipboard_content:
                    self._process_new_content(current_content)
                    self.last_clipboard_content = current_content

            except Exception as e:
                print(f"Error monitoring clipboard: {e}")

            # Sleep to avoid excessive CPU usage
            time.sleep(0.5)

    def _process_new_content(self, content):
        """Process new clipboard content and store it in database."""
        if not content or not content.strip():
            return  # Skip empty content

        try:
            # For now, we only handle text content (simple version)
            content_type = "text"

            # Store in database
            self.database.add_item(
                content_type=content_type, content=content, timestamp=datetime.now()
            )

            # Emit signal to update UI
            self.new_item_signal.emit()

            print(
                f"New clipboard item stored: {content[:50]}{'...' if len(content) > 50 else ''}"
            )

        except Exception as e:
            print(f"Error processing clipboard content: {e}")

    def get_current_clipboard(self):
        """Get current clipboard content."""
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Error getting clipboard content: {e}")
            return ""

    def set_clipboard(self, content):
        """Set clipboard content."""
        try:
            pyperclip.copy(content)
            return True
        except Exception as e:
            print(f"Error setting clipboard content: {e}")
            return False
