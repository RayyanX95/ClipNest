"""
User Interface module for ClipNest.
"""

from datetime import datetime

import pyperclip
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSplitter,
    QSystemTrayIcon,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class ClipNestItemWidget(QWidget):
    """Custom widget for displaying clipboard items in the list."""

    def __init__(self, item_data, is_dark=True):
        super().__init__()
        self.item_data = item_data
        self.is_dark = is_dark
        self.setup_ui()

    def setup_ui(self):
        """Setup the item widget UI."""
        # Card container layout
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(16, 4, 16, 4)  # Add spacing left/right
        card_layout.setSpacing(0)

        # Card widget for background (no border)
        card_widget = QWidget()
        card_widget_layout = QVBoxLayout()
        card_widget_layout.setContentsMargins(12, 8, 12, 8)
        card_widget_layout.setSpacing(4)

        # Content preview (first 100 characters)
        content = self.item_data["content"]
        preview = content[:100] + "..." if len(content) > 100 else content

        # Choose text colors and background based on theme
        if self.is_dark:
            main_color = "#f0f0f0"
            info_color = "#cccccc"
            bg_color = "#343434"
            hover_bg_color = "#464646"
            border = "none"
        else:
            main_color = "#232629"
            info_color = "#555555"
            bg_color = "#ede6e6"
            hover_bg_color = "#ffffff"
            border = "none"

        # Content label
        content_label = QLabel(preview)
        content_label.setWordWrap(True)
        content_label.setTextFormat(Qt.TextFormat.PlainText)
        content_label.setStyleSheet(
            f"QLabel {{ color: {main_color} !important; font-size: 13px; background: transparent; }}"
        )

        # Info label (timestamp, type, favorite)
        from datetime import datetime

        timestamp = datetime.fromisoformat(self.item_data["timestamp"]).strftime(
            "%m/%d %H:%M"
        )
        info_text = f"{timestamp} • {self.item_data['content_type']}"
        if self.item_data["is_favorite"]:
            info_text += " • ⭐"
        info_label = QLabel(info_text)
        info_label.setStyleSheet(
            f"QLabel {{ color: {info_color} !important; font-size: 10px; background: transparent; }}"
        )

        card_widget_layout.addWidget(content_label)
        card_widget_layout.addWidget(info_label)
        card_widget.setLayout(card_widget_layout)
        card_widget.setStyleSheet(
            f"""    
            QWidget {{
            background: {bg_color};
            border: {border};
            border-radius: 10px;
            cursor: pointer;
            }}
            QWidget:hover {{
            background: {hover_bg_color};
            }}
            """
        )

        card_layout.addWidget(card_widget)
        self.setLayout(card_layout)
        self.setStyleSheet("background: transparent;")


class ClipNestUI(QMainWindow):
    """Main UI window for ClipNest."""

    def __init__(self, database, is_dark=True):
        super().__init__()
        self.database = database
        self.tray_icon = None
        self.is_dark = is_dark
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        """Setup the main UI components."""
        self.setWindowTitle("ClipNest")
        self.setGeometry(100, 100, 600, 500)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search clipboard history...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # History list
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_item_clicked)
        self.history_list.itemDoubleClicked.connect(self.on_item_double_clicked)
        # Set custom selection color for light theme
        self.history_list.setStyleSheet(
            """
            QListWidget::item:selected {
                background: transparent;
                color: #232629;
                border-radius: 10px;
            }
            QListWidget::item:focus {
                outline: none;
            }
            """
        )
        layout.addWidget(self.history_list)

        # Button layout
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh_history)

        self.clear_btn = QPushButton("Clear History")
        self.clear_btn.clicked.connect(self.clear_history)

        self.favorite_btn = QPushButton("Toggle Favorite")
        self.favorite_btn.clicked.connect(self.toggle_favorite)

        button_layout.addWidget(self.refresh_btn)
        button_layout.addWidget(self.favorite_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)

        # Load initial history
        self.refresh_history()

        # Hide window initially (will be shown via system tray)
        self.hide()

    def setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        # You can add global shortcuts here later
        pass

    def setup_menubar(self):
        """Setup system tray icon and menu with light/dark mode support."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(
                None, "System Tray", "System tray is not available on this system."
            )
            return

        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)

        # Robust icon path resolution for PyInstaller bundle
        import os
        import subprocess
        import sys

        if getattr(sys, "frozen", False):
            # PyInstaller bundle: use _MEIPASS if available
            icon_dir = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        else:
            icon_dir = os.path.dirname(os.path.abspath(__file__))
        light_icon_path = os.path.join(icon_dir, "clip_app_icon_light.png")
        dark_icon_path = os.path.join(icon_dir, "clip_app_icon_dark.png")
        icon_path = light_icon_path
        try:
            result = subprocess.run(
                ["defaults", "read", "-g", "AppleInterfaceStyle"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and "Dark" in result.stdout:
                icon_path = dark_icon_path
        except Exception as e:
            print(f"Could not detect system appearance: {e}")
        icon = QIcon(icon_path)
        if icon.isNull():
            print(
                f"Warning: Failed to load tray icon '{icon_path}'. Check the file path and PNG validity."
            )
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("ClipNest")

        # Create tray menu
        tray_menu = QMenu()

        show_action = QAction("Show ClipNest", self)
        show_action.triggered.connect(self.show_window)
        tray_menu.addAction(show_action)

        tray_menu.addSeparator()

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    def on_tray_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_window()

    def show_window(self):
        """Show and raise the main window."""
        self.show()
        self.raise_()
        self.activateWindow()

    def quit_application(self):
        """Quit the application."""
        QApplication.instance().quit()

    def refresh_history(self):
        """Refresh the history list from database."""
        try:
            self.history_list.clear()

            # Get history from database
            history = self.database.get_history(100)

            for row in history:
                item_data = {
                    "id": row["id"],
                    "content_type": row["content_type"],
                    "content": row["content"],
                    "timestamp": row["timestamp"],
                    "is_favorite": row["is_favorite"],
                }

                # Create list item
                list_item = QListWidgetItem()

                # Create custom widget with theme info
                item_widget = ClipNestItemWidget(item_data, is_dark=self.is_dark)

                # Set the widget and store data
                list_item.setSizeHint(item_widget.sizeHint())
                list_item.setData(Qt.ItemDataRole.UserRole, item_data)

                self.history_list.addItem(list_item)
                self.history_list.setItemWidget(list_item, item_widget)

            # Update status
            stats = self.database.get_stats()
            self.status_label.setText(
                f"Total items: {stats.get('total_items', 0)} | "
                f"Favorites: {stats.get('favorite_items', 0)}"
            )

        except Exception as e:
            print(f"Error refreshing history: {e}")
            self.status_label.setText(f"Error: {e}")

    def on_search_changed(self, text):
        """Handle search input changes."""
        if not text.strip():
            self.refresh_history()
            return

        try:
            self.history_list.clear()

            # Search in database
            results = self.database.search_items(text, 50)

            for row in results:
                item_data = {
                    "id": row["id"],
                    "content_type": row["content_type"],
                    "content": row["content"],
                    "timestamp": row["timestamp"],
                    "is_favorite": row["is_favorite"],
                }

                # Create list item
                list_item = QListWidgetItem()

                # Create custom widget with theme info
                item_widget = ClipNestItemWidget(item_data, is_dark=self.is_dark)

                # Set the widget and store data
                list_item.setSizeHint(item_widget.sizeHint())
                list_item.setData(Qt.ItemDataRole.UserRole, item_data)

                self.history_list.addItem(list_item)
                self.history_list.setItemWidget(list_item, item_widget)

            self.status_label.setText(f"Found {len(results)} items")

        except Exception as e:
            print(f"Error searching: {e}")

    def on_item_clicked(self, item):
        """Handle single click on history item - copy to clipboard."""
        try:
            item_data = item.data(Qt.ItemDataRole.UserRole)
            content = item_data["content"]

            # Copy to clipboard
            pyperclip.copy(content)

            self.status_label.setText("Copied to clipboard!")

            # Clear status after 2 seconds
            QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))

        except Exception as e:
            print(f"Error copying item: {e}")
            self.status_label.setText(f"Error copying: {e}")

    def on_item_double_clicked(self, item):
        """Handle double click on history item."""
        # For now, just copy (same as single click)
        # In a more advanced version, this could paste directly
        self.on_item_clicked(item)

    def toggle_favorite(self):
        """Toggle favorite status of selected item."""
        current_item = self.history_list.currentItem()
        if not current_item:
            self.status_label.setText("No item selected")
            return

        try:
            item_data = current_item.data(Qt.ItemDataRole.UserRole)
            item_id = item_data["id"]

            success = self.database.toggle_favorite(item_id)
            if success:
                self.refresh_history()
                self.status_label.setText("Favorite toggled!")
                QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
            else:
                self.status_label.setText("Error toggling favorite")

        except Exception as e:
            print(f"Error toggling favorite: {e}")
            self.status_label.setText(f"Error: {e}")

    def clear_history(self):
        """Clear clipboard history (keeping favorites)."""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Clear all clipboard history? (Favorites will be kept)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.database.clear_history(keep_favorites=True)
                if success:
                    self.refresh_history()
                    self.status_label.setText("History cleared!")
                    QTimer.singleShot(2000, lambda: self.status_label.setText("Ready"))
                else:
                    self.status_label.setText("Error clearing history")

            except Exception as e:
                print(f"Error clearing history: {e}")
                self.status_label.setText(f"Error: {e}")

    def closeEvent(self, event):
        """Handle window close event - hide instead of quit."""
        if self.tray_icon and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            event.accept()
