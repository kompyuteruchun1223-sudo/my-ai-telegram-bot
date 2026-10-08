import asyncio
import sqlite3
from datetime import datetime, timezone


class Database:
    def __init__(self, path: str):
        self.path = path

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA foreign_keys=ON;")
        return connection

    def _initialize_sync(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    created_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_messages_user_id_timestamp
                ON messages(user_id, timestamp);
                """
            )

    async def initialize(self) -> None:
        await asyncio.to_thread(self._initialize_sync)

    def _upsert_user_sync(
        self,
        user_id: int,
        first_name: str | None,
        last_name: str | None,
        username: str | None,
    ) -> None:
        now = self._now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO users (
                    user_id, first_name, last_name, username, created_at, last_seen_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                    first_name=excluded.first_name,
                    last_name=excluded.last_name,
                    username=excluded.username,
                    last_seen_at=excluded.last_seen_at
                """,
                (user_id, first_name, last_name, username, now, now),
            )

    async def upsert_user(
        self,
        user_id: int,
        first_name: str | None,
        last_name: str | None,
        username: str | None,
    ) -> None:
        await asyncio.to_thread(
            self._upsert_user_sync,
            user_id,
            first_name,
            last_name,
            username,
        )

    def _add_message_sync(self, user_id: int, role: str, message: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO messages (user_id, role, message, timestamp)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, role, message, self._now()),
            )

    async def add_message(self, user_id: int, role: str, message: str) -> None:
        await asyncio.to_thread(self._add_message_sync, user_id, role, message)

    def _get_history_sync(self, user_id: int, limit: int) -> list[dict[str, str]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT role, message
                FROM messages
                WHERE user_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (user_id, limit),
            ).fetchall()

        rows.reverse()
        return [
            {"role": row["role"], "message": row["message"]}
            for row in rows
        ]

    async def get_history(self, user_id: int, limit: int) -> list[dict[str, str]]:
        return await asyncio.to_thread(self._get_history_sync, user_id, limit)

    def _clear_history_sync(self, user_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))

    async def clear_history(self, user_id: int) -> None:
        await asyncio.to_thread(self._clear_history_sync, user_id)

    def _get_stats_sync(self) -> dict[str, int]:
        today = datetime.now(timezone.utc).date().isoformat()

        with self._connect() as conn:
            total_users = conn.execute(
                "SELECT COUNT(*) FROM users"
            ).fetchone()[0]

            today_users = conn.execute(
                """
                SELECT COUNT(*)
                FROM users
                WHERE substr(last_seen_at, 1, 10) = ?
                """,
                (today,),
            ).fetchone()[0]

            total_messages = conn.execute(
                "SELECT COUNT(*) FROM messages"
            ).fetchone()[0]

        return {
            "total_users": int(total_users),
            "today_users": int(today_users),
            "total_messages": int(total_messages),
        }

    async def get_stats(self) -> dict[str, int]:
        return await asyncio.to_thread(self._get_stats_sync)

    async def close(self) -> None:
        return
