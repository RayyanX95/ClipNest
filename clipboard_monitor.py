"""
Clipboard monitoring module for detecting and processing clipboard changes for ClipNest.
"""

import os
from datetime import datetime

import pyperclip
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage
from PyQt6.QtWidgets import QApplication


class ClipNestMonitor(QObject):
    """Monitor system clipboard for changes and store new items for ClipNest."""

    # Signal emitted when a new item is added to clipboard
    new_item_signal = pyqtSignal()

    def __init__(self, database):
        super().__init__()
        self.database = database
        self.monitoring = False
        self.last_clipboard_data = None
        self.clipboard = QApplication.instance().clipboard()
        self.clipboard.dataChanged.connect(self._on_clipboard_change)

    def start_monitoring(self):
        """Start monitoring clipboard changes."""
        # No thread needed, handled by Qt signal
        print("Clipboard monitoring started (Qt events)")

    def stop_monitoring(self):
        """Stop clipboard monitoring."""
        print("Clipboard monitoring stopped")

    def _on_clipboard_change(self):
        """Handle clipboard data changes."""
        md = self.clipboard.mimeData()
        if md.hasImage():
            image = self.clipboard.image()
            if not image.isNull():
                # Save image to file
                img_dir = os.path.expanduser("~/.clipboard_manager/images")
                os.makedirs(img_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                img_path = os.path.join(img_dir, f"clipnest_{timestamp}.png")
                image.save(img_path, "PNG")
                self.database.add_item(
                    content_type="image", content=img_path, timestamp=datetime.now()
                )
                self.new_item_signal.emit()
        elif md.hasText():
            text = md.text()
            if text and text.strip() and text != self.last_clipboard_data:
                self.database.add_item(
                    content_type="text", content=text, timestamp=datetime.now()
                )
                self.last_clipboard_data = text
                self.new_item_signal.emit()

    def get_current_clipboard(self):
        """Get current clipboard content."""
        md = self.clipboard.mimeData()
        if md.hasImage():
            return self.clipboard.image()
        elif md.hasText():
            return md.text()
        return None

    def set_clipboard(self, content, content_type="text"):
        """Set clipboard content."""
        if content_type == "image":
            image = QImage(content)
            if not image.isNull():
                self.clipboard.setImage(image)
                return True
            return False
        else:
            self.clipboard.setText(content)
            return True
