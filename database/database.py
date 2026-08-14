import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).parent / "remotedm.db"


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

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS friend_aliases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            friend_id INTEGER NOT NULL,
            alias TEXT NOT NULL,
            UNIQUE(friend_id, alias),
            FOREIGN KEY (friend_id)
                REFERENCES friends(id)
                ON DELETE CASCADE
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_discord_user_id TEXT NOT NULL,
            recipient_discord_user_id TEXT,
            direction TEXT NOT NULL,
            content TEXT NOT NULL,
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


def is_registered(discord_user_id: int):
    connection = get_connection()

    friend = connection.execute(
        """
        SELECT 1
        FROM friends
        WHERE discord_user_id = ?
        AND opted_in = 1
        """,
        (str(discord_user_id),),
    ).fetchone()

    connection.close()

    return friend is not None


def get_registered_friends():
    connection = get_connection()

    friends = connection.execute(
        """
        SELECT discord_user_id, display_name
        FROM friends
        WHERE opted_in = 1
        ORDER BY display_name
        """
    ).fetchall()

    connection.close()

    return friends


def add_alias(discord_user_id: int, alias: str):
    connection = get_connection()

    friend = connection.execute(
        """
        SELECT id
        FROM friends
        WHERE discord_user_id = ?
        AND opted_in = 1
        """,
        (str(discord_user_id),),
    ).fetchone()

    if friend is None:
        connection.close()
        return False

    normalized_alias = alias.strip().casefold()

    if not normalized_alias:
        connection.close()
        return False

    connection.execute(
        """
        INSERT OR IGNORE INTO friend_aliases (friend_id, alias)
        VALUES (?, ?)
        """,
        (friend["id"], normalized_alias),
    )

    connection.commit()
    connection.close()


def find_friend(name: str):
    connection = get_connection()

    search = name.strip().casefold()

    friend = connection.execute(
        """
        SELECT f.discord_user_id, f.display_name
        FROM friends f
        WHERE f.opted_in = 1
        AND (
            lower(f.display_name) = ?
            OR EXISTS (
                SELECT 1
                FROM friend_aliases a
                WHERE a.friend_id = f.id
                AND a.alias = ?
            )
        )
        LIMIT 1
        """,
        (search, search),
    ).fetchone()

    connection.close()

    return friend


def save_message(
    sender_discord_user_id: int,
    recipient_discord_user_id: int | None,
    direction: str,
    content: str,
):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO messages (
            sender_discord_user_id,
            recipient_discord_user_id,
            direction,
            content
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            str(sender_discord_user_id),
            (
                str(recipient_discord_user_id)
                if recipient_discord_user_id is not None
                else None
            ),
            direction,
            content,
        ),
    )

    connection.commit()
    connection.close()


def get_messages(
    discord_user_id: int,
    limit: int = 50,
):
    connection = get_connection()

    messages = connection.execute(
        """
        SELECT
            id,
            sender_discord_user_id,
            recipient_discord_user_id,
            direction,
            content,
            created_at
        FROM messages
        WHERE
            sender_discord_user_id = ?
            OR recipient_discord_user_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            str(discord_user_id),
            str(discord_user_id),
            limit,
        ),
    ).fetchall()

    connection.close()

    return messages

def get_conversation(
    discord_user_id: int,
    limit: int = 100,
):
    connection = get_connection()

    messages = connection.execute(
        """
        SELECT
            id,
            sender_discord_user_id,
            recipient_discord_user_id,
            direction,
            content,
            created_at
        FROM messages
        WHERE
            sender_discord_user_id = ?
            OR recipient_discord_user_id = ?
        ORDER BY id ASC
        LIMIT ?
        """,
        (
            str(discord_user_id),
            str(discord_user_id),
            limit,
        ),
    ).fetchall()

    connection.close()

    return messages

def archive_and_unregister(discord_user_id: int):
    active_connection = get_connection()

    friend = active_connection.execute(
        """
        SELECT id, discord_user_id, display_name, created_at
        FROM friends
        WHERE discord_user_id = ?
        """,
        (str(discord_user_id),),
    ).fetchone()

    if friend is None:
        active_connection.close()
        return False

    aliases = active_connection.execute(
        """
        SELECT alias
        FROM friend_aliases
        WHERE friend_id = ?
        ORDER BY alias
        """,
        (friend["id"],),
    ).fetchall()

    history_path = DATABASE_PATH.parent / "history.db"

    history_connection = sqlite3.connect(history_path)

    history_connection.execute(
        """
        CREATE TABLE IF NOT EXISTS registration_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discord_user_id TEXT NOT NULL,
            display_name TEXT NOT NULL,
            aliases TEXT,
            registered_at TEXT NOT NULL,
            unregistered_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    alias_text = ", ".join(alias["alias"] for alias in aliases)

    history_connection.execute(
        """
        INSERT INTO registration_history (
            discord_user_id,
            display_name,
            aliases,
            registered_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            friend["discord_user_id"],
            friend["display_name"],
            alias_text,
            friend["created_at"],
        ),
    )

    history_connection.commit()
    history_connection.close()

    active_connection.execute(
        """
        DELETE FROM friends
        WHERE discord_user_id = ?
        """,
        (str(discord_user_id),),
    )

    active_connection.commit()
    active_connection.close()

    return 