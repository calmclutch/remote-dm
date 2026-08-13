import sqlite3
from pathlib import Path

DATABASE_PATH = Path(__file__).parent.parent / "database" / "remotedm.db"


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    connection = get_connection()

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            opted_in INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def register_friend(discord_user_id: int, display_name: str):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO friends (
            discord_user_id,
            display_name,
            opted_in
        )
        VALUES (?, ?, 1)
        ON CONFLICT(discord_user_id)
        DO UPDATE SET
            display_name = excluded.display_name,
            opted_in = 1
        """,
        (str(discord_user_id), display_name),
    )

    connection.commit()
    connection.close()