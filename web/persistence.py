"""SQLite-backed persistence for TorchCoder web accounts and progress."""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

DB_PATH = Path(os.environ.get("TORCHCODER_DB_PATH", "data/torchcoder.db"))
SESSION_TTL_DAYS = int(os.environ.get("SESSION_TTL_DAYS", "30"))
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ts(dt: datetime | None = None) -> str:
    return (dt or _utcnow()).isoformat()


def _connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_login_at TEXT
            );

            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_user_id
            ON sessions(user_id);

            CREATE TABLE IF NOT EXISTS user_task_progress (
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                task_id TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'todo',
                attempts INTEGER NOT NULL DEFAULT 0,
                best_time REAL,
                solved_at TEXT,
                draft_code TEXT,
                draft_updated_at TEXT,
                last_opened_at TEXT,
                PRIMARY KEY (user_id, task_id)
            );

            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
                current_task_id TEXT,
                updated_at TEXT NOT NULL
            );
            """
        )


def _validate_username(username: str) -> str:
    cleaned = username.strip()
    if not USERNAME_PATTERN.fullmatch(cleaned):
        raise ValueError("用户名长度必须为 3 到 32 位，只能包含字母、数字、点号、下划线或短横线。")
    return cleaned


def _validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("密码长度至少需要 8 位。")
    return password


def _hash_password(password: str, *, salt: bytes | None = None, iterations: int = 200_000) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{iterations}${salt.hex()}${digest.hex()}"


def _verify_password(password: str, encoded: str) -> bool:
    try:
        iterations_s, salt_hex, digest_hex = encoded.split("$", 2)
        candidate = _hash_password(
            password,
            salt=bytes.fromhex(salt_hex),
            iterations=int(iterations_s),
        )
    except Exception:
        return False
    return hmac.compare_digest(candidate, encoded)


def _cleanup_expired_sessions(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM sessions WHERE expires_at <= ?", (_ts(),))


def _row_to_user(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "created_at": row["created_at"],
        "last_login_at": row["last_login_at"],
        "current_task_id": row["current_task_id"],
    }


def create_user(username: str, password: str) -> dict[str, Any]:
    clean_username = _validate_username(username)
    _validate_password(password)
    created_at = _ts()

    with _connect() as conn:
        try:
            cursor = conn.execute(
                """
                INSERT INTO users (username, password_hash, created_at, last_login_at)
                VALUES (?, ?, ?, ?)
                """,
                (clean_username, _hash_password(password), created_at, created_at),
            )
        except sqlite3.IntegrityError as exc:
            raise ValueError("用户名已被占用。") from exc

        user_id = int(cursor.lastrowid)
        conn.execute(
            """
            INSERT INTO user_preferences (user_id, current_task_id, updated_at)
            VALUES (?, NULL, ?)
            """,
            (user_id, created_at),
        )
        conn.commit()

    return {
        "id": user_id,
        "username": clean_username,
        "created_at": created_at,
        "last_login_at": created_at,
        "current_task_id": None,
    }


def authenticate_user(username: str, password: str) -> dict[str, Any] | None:
    clean_username = username.strip()
    if not clean_username or not password:
        return None

    with _connect() as conn:
        row = conn.execute(
            """
            SELECT u.id, u.username, u.password_hash, u.created_at, u.last_login_at, p.current_task_id
            FROM users u
            LEFT JOIN user_preferences p ON p.user_id = u.id
            WHERE u.username = ? COLLATE NOCASE
            """,
            (clean_username,),
        ).fetchone()

        if row is None or not _verify_password(password, row["password_hash"]):
            return None

        last_login_at = _ts()
        conn.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (last_login_at, row["id"]),
        )
        conn.commit()

    return {
        "id": row["id"],
        "username": row["username"],
        "created_at": row["created_at"],
        "last_login_at": last_login_at,
        "current_task_id": row["current_task_id"],
    }


def create_session(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    created_at = _utcnow()
    expires_at = created_at + timedelta(days=SESSION_TTL_DAYS)

    with _connect() as conn:
        _cleanup_expired_sessions(conn)
        conn.execute(
            """
            INSERT INTO sessions (token, user_id, created_at, expires_at)
            VALUES (?, ?, ?, ?)
            """,
            (token, user_id, _ts(created_at), _ts(expires_at)),
        )
        conn.commit()

    return token


def get_user_by_session(token: str | None) -> dict[str, Any] | None:
    if not token:
        return None

    with _connect() as conn:
        _cleanup_expired_sessions(conn)
        row = conn.execute(
            """
            SELECT u.id, u.username, u.created_at, u.last_login_at, p.current_task_id
            FROM sessions s
            JOIN users u ON u.id = s.user_id
            LEFT JOIN user_preferences p ON p.user_id = u.id
            WHERE s.token = ?
            """,
            (token,),
        ).fetchone()
        conn.commit()

    return _row_to_user(row)


def delete_session(token: str | None) -> None:
    if not token:
        return
    with _connect() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()


def set_current_task(user_id: int, task_id: str | None) -> None:
    updated_at = _ts()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO user_preferences (user_id, current_task_id, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                current_task_id = excluded.current_task_id,
                updated_at = excluded.updated_at
            """,
            (user_id, task_id, updated_at),
        )
        conn.commit()


def get_progress_map(user_id: int) -> dict[str, dict[str, Any]]:
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT task_id, status, attempts, best_time, solved_at, draft_code, draft_updated_at, last_opened_at
            FROM user_task_progress
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchall()

    progress: dict[str, dict[str, Any]] = {}
    for row in rows:
        progress[row["task_id"]] = {
            "status": row["status"],
            "attempts": row["attempts"],
            "best_time": row["best_time"],
            "solved_at": row["solved_at"],
            "draft_code": row["draft_code"],
            "draft_updated_at": row["draft_updated_at"],
            "last_opened_at": row["last_opened_at"],
        }
    return progress


def get_task_state(user_id: int, task_id: str) -> dict[str, Any]:
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT status, attempts, best_time, solved_at, draft_code, draft_updated_at, last_opened_at
            FROM user_task_progress
            WHERE user_id = ? AND task_id = ?
            """,
            (user_id, task_id),
        ).fetchone()

    if row is None:
        return {
            "status": "todo",
            "attempts": 0,
            "best_time": None,
            "solved_at": None,
            "draft_code": None,
            "draft_updated_at": None,
            "last_opened_at": None,
        }

    return {
        "status": row["status"],
        "attempts": row["attempts"],
        "best_time": row["best_time"],
        "solved_at": row["solved_at"],
        "draft_code": row["draft_code"],
        "draft_updated_at": row["draft_updated_at"],
        "last_opened_at": row["last_opened_at"],
    }


def save_task_draft(user_id: int, task_id: str, code: str) -> str:
    saved_at = _ts()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO user_task_progress (
                user_id, task_id, status, attempts, draft_code, draft_updated_at, last_opened_at
            )
            VALUES (?, ?, 'todo', 0, ?, ?, ?)
            ON CONFLICT(user_id, task_id) DO UPDATE SET
                draft_code = excluded.draft_code,
                draft_updated_at = excluded.draft_updated_at,
                last_opened_at = excluded.last_opened_at
            """,
            (user_id, task_id, code, saved_at, saved_at),
        )
        conn.execute(
            """
            INSERT INTO user_preferences (user_id, current_task_id, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                current_task_id = excluded.current_task_id,
                updated_at = excluded.updated_at
            """,
            (user_id, task_id, saved_at),
        )
        conn.commit()

    return saved_at


def touch_task(user_id: int, task_id: str) -> None:
    opened_at = _ts()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO user_task_progress (
                user_id, task_id, status, attempts, last_opened_at
            )
            VALUES (?, ?, 'todo', 0, ?)
            ON CONFLICT(user_id, task_id) DO UPDATE SET
                last_opened_at = excluded.last_opened_at
            """,
            (user_id, task_id, opened_at),
        )
        conn.execute(
            """
            INSERT INTO user_preferences (user_id, current_task_id, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                current_task_id = excluded.current_task_id,
                updated_at = excluded.updated_at
            """,
            (user_id, task_id, opened_at),
        )
        conn.commit()


def record_submission(user_id: int, task_id: str, code: str, solved: bool, total_time: float) -> dict[str, Any]:
    now = _ts()
    current = get_task_state(user_id, task_id)
    attempts = current["attempts"] + 1

    if solved:
        status = "solved"
        if current["best_time"] is None:
            best_time = total_time
        else:
            best_time = min(float(current["best_time"]), total_time)
        solved_at = current["solved_at"] or now
    else:
        status = "solved" if current["status"] == "solved" else "attempted"
        best_time = current["best_time"]
        solved_at = current["solved_at"]

    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO user_task_progress (
                user_id, task_id, status, attempts, best_time, solved_at,
                draft_code, draft_updated_at, last_opened_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, task_id) DO UPDATE SET
                status = excluded.status,
                attempts = excluded.attempts,
                best_time = excluded.best_time,
                solved_at = excluded.solved_at,
                draft_code = excluded.draft_code,
                draft_updated_at = excluded.draft_updated_at,
                last_opened_at = excluded.last_opened_at
            """,
            (
                user_id,
                task_id,
                status,
                attempts,
                best_time,
                solved_at,
                code,
                now,
                now,
            ),
        )
        conn.execute(
            """
            INSERT INTO user_preferences (user_id, current_task_id, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                current_task_id = excluded.current_task_id,
                updated_at = excluded.updated_at
            """,
            (user_id, task_id, now),
        )
        conn.commit()

    return {
        "status": status,
        "attempts": attempts,
        "best_time": best_time,
        "solved_at": solved_at,
        "draft_updated_at": now,
    }


def reset_user_progress(user_id: int) -> None:
    with _connect() as conn:
        conn.execute("DELETE FROM user_task_progress WHERE user_id = ?", (user_id,))
        conn.execute(
            """
            INSERT INTO user_preferences (user_id, current_task_id, updated_at)
            VALUES (?, NULL, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                current_task_id = NULL,
                updated_at = excluded.updated_at
            """,
            (user_id, _ts()),
        )
        conn.commit()
