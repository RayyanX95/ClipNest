"""
Database module for persistent storage of clipboard history.
"""

import os
import sqlite3
from datetime import datetime
from typing import List, Optional, Tuple


class ClipboardDatabase:
    """Handle SQLite database operations for clipboard history."""

    def __init__(self, db_path=None):
        """Initialize database connection and create tables if needed."""
        if db_path is None:
            # Store database in user's home directory
            home_dir = os.path.expanduser("~")
            app_dir = os.path.join(home_dir, ".clipboard_manager")
            os.makedirs(app_dir, exist_ok=True)
            db_path = os.path.join(app_dir, "clipboard_history.db")

        self.db_path = db_path
        self.connection = None
        self.history_limit = 200  # Default limit

        self._connect()
        self._create_tables()

    def _connect(self):
        """Establish database connection."""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable column access by name
            print(f"Connected to database: {self.db_path}")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def _create_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            cursor = self.connection.cursor()

            # Main clipboard items table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS clipboard_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    is_favorite BOOLEAN DEFAULT FALSE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            # Create index for faster queries
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON clipboard_items(timestamp DESC)
            """
            )

            self.connection.commit()
            print("Database tables created/verified")

        except Exception as e:
            print(f"Error creating database tables: {e}")
            raise

    def add_item(self, content_type: str, content: str, timestamp: datetime) -> bool:
        """Add a new clipboard item to the database."""
        try:
            # Check if this exact content already exists recently
            if self._is_duplicate(content):
                return False

            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO clipboard_items (content_type, content, timestamp)
                VALUES (?, ?, ?)
            """,
                (content_type, content, timestamp),
            )

            self.connection.commit()

            # Enforce history limit
            self._enforce_history_limit()

            return True

        except Exception as e:
            print(f"Error adding item to database: {e}")
            return False

    def _is_duplicate(self, content: str, time_window_minutes: int = 1) -> bool:
        """Check if content is a duplicate within the time window."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT COUNT(*) FROM clipboard_items 
                WHERE content = ? 
                AND datetime(timestamp) > datetime('now', '-{} minutes')
            """.format(
                    time_window_minutes
                ),
                (content,),
            )

            count = cursor.fetchone()[0]
            return count > 0

        except Exception as e:
            print(f"Error checking for duplicates: {e}")
            return False

    def _enforce_history_limit(self):
        """Remove oldest items if history exceeds the limit."""
        try:
            cursor = self.connection.cursor()

            # Count total items
            cursor.execute("SELECT COUNT(*) FROM clipboard_items")
            total_items = cursor.fetchone()[0]

            if total_items > self.history_limit:
                # Delete oldest items (keeping favorites)
                items_to_delete = total_items - self.history_limit
                cursor.execute(
                    """
                    DELETE FROM clipboard_items 
                    WHERE id IN (
                        SELECT id FROM clipboard_items 
                        WHERE is_favorite = FALSE 
                        ORDER BY timestamp ASC 
                        LIMIT ?
                    )
                """,
                    (items_to_delete,),
                )

                self.connection.commit()
                print(f"Cleaned up {cursor.rowcount} old items")

        except Exception as e:
            print(f"Error enforcing history limit: {e}")

    def get_history(self, limit: int = 50) -> List[Tuple]:
        """Get clipboard history ordered by most recent first."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                SELECT id, content_type, content, timestamp, is_favorite
                FROM clipboard_items 
                ORDER BY is_favorite DESC, timestamp DESC 
                LIMIT ?
            """,
                (limit,),
            )

            return cursor.fetchall()

        except Exception as e:
            print(f"Error getting history: {e}")
            return []

    def search_items(self, query: str, limit: int = 50) -> List[Tuple]:
        """Search clipboard items by content."""
        try:
            cursor = self.connection.cursor()
            search_pattern = f"%{query}%"
            cursor.execute(
                """
                SELECT id, content_type, content, timestamp, is_favorite
                FROM clipboard_items 
                WHERE content LIKE ? 
                ORDER BY is_favorite DESC, timestamp DESC 
                LIMIT ?
            """,
                (search_pattern, limit),
            )

            return cursor.fetchall()

        except Exception as e:
            print(f"Error searching items: {e}")
            return []

    def toggle_favorite(self, item_id: int) -> bool:
        """Toggle favorite status of an item."""
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                """
                UPDATE clipboard_items 
                SET is_favorite = NOT is_favorite 
                WHERE id = ?
            """,
                (item_id,),
            )

            self.connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error toggling favorite: {e}")
            return False

    def delete_item(self, item_id: int) -> bool:
        """Delete a specific item from history."""
        try:
            cursor = self.connection.cursor()
            cursor.execute("DELETE FROM clipboard_items WHERE id = ?", (item_id,))

            self.connection.commit()
            return cursor.rowcount > 0

        except Exception as e:
            print(f"Error deleting item: {e}")
            return False

    def clear_history(self, keep_favorites: bool = True) -> bool:
        """Clear clipboard history."""
        try:
            cursor = self.connection.cursor()

            if keep_favorites:
                cursor.execute("DELETE FROM clipboard_items WHERE is_favorite = FALSE")
            else:
                cursor.execute("DELETE FROM clipboard_items")

            self.connection.commit()
            print(f"Cleared {cursor.rowcount} items from history")
            return True

        except Exception as e:
            print(f"Error clearing history: {e}")
            return False

    def get_stats(self) -> dict:
        """Get database statistics."""
        try:
            cursor = self.connection.cursor()

            cursor.execute("SELECT COUNT(*) FROM clipboard_items")
            total_items = cursor.fetchone()[0]

            cursor.execute(
                "SELECT COUNT(*) FROM clipboard_items WHERE is_favorite = TRUE"
            )
            favorite_items = cursor.fetchone()[0]

            return {
                "total_items": total_items,
                "favorite_items": favorite_items,
                "history_limit": self.history_limit,
            }

        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}

    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("Database connection closed")
