"""SQLite persistence for active GuessGame instances."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from pathlib import Path

from app.guess_game import GuessGame


class GameStorage:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _create_table(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS games (
                    chat_id INTEGER PRIMARY KEY,
                    secret INTEGER NOT NULL,
                    attempts INTEGER NOT NULL,
                    guesses TEXT NOT NULL,
                    finished INTEGER NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS game_stats (
                    chat_id INTEGER PRIMARY KEY,
                    wins INTEGER NOT NULL DEFAULT 0,
                    losses INTEGER NOT NULL DEFAULT 0,
                    total_attempts INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS players (
                    chat_id INTEGER PRIMARY KEY,
                    display_name TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS learning_progress (
                    chat_id INTEGER NOT NULL,
                    day_number INTEGER NOT NULL,
                    completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (chat_id, day_number)
                )
                """
            )

    def save_player(self, chat_id: int, display_name: str) -> None:
        display_name = display_name.strip() or f"Игрок {chat_id}"
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """
                INSERT INTO players (chat_id, display_name)
                VALUES (?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    display_name = excluded.display_name
                """,
                (chat_id, display_name),
            )

    def mark_learning_day(self, chat_id: int, day_number: int) -> bool:
        if day_number < 1:
            raise ValueError("Номер учебного дня должен быть положительным")

        with closing(self._connect()) as connection, connection:
            cursor = connection.execute(
                """
                INSERT OR IGNORE INTO learning_progress (chat_id, day_number)
                VALUES (?, ?)
                """,
                (chat_id, day_number),
            )
        return cursor.rowcount == 1

    def get_completed_learning_days(self, chat_id: int) -> list[int]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT day_number
                FROM learning_progress
                WHERE chat_id = ?
                ORDER BY day_number
                """,
                (chat_id,),
            ).fetchall()
        return [day_number for (day_number,) in rows]

    def save(self, chat_id: int, game: GuessGame) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """
                INSERT INTO games (chat_id, secret, attempts, guesses, finished)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    secret = excluded.secret,
                    attempts = excluded.attempts,
                    guesses = excluded.guesses,
                    finished = excluded.finished
                """,
                (
                    chat_id,
                    game.secret,
                    game.attempts,
                    json.dumps(game.guesses),
                    int(game.finished),
                ),
            )

    def load_all(self) -> dict[int, GuessGame]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT chat_id, secret, attempts, guesses, finished FROM games"
            ).fetchall()

        games: dict[int, GuessGame] = {}
        for chat_id, secret, attempts, guesses_json, finished in rows:
            game = GuessGame(secret=secret)
            game.attempts = attempts
            game.guesses = json.loads(guesses_json)
            game.finished = bool(finished)
            games[chat_id] = game
        return games

    def record_result(self, chat_id: int, result: str, attempts: int) -> None:
        wins = int(result == "win")
        losses = int(result == "lose")
        if wins == 0 and losses == 0:
            raise ValueError("Статистику можно записать только для win или lose")

        with closing(self._connect()) as connection, connection:
            connection.execute(
                """
                INSERT INTO game_stats (chat_id, wins, losses, total_attempts)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(chat_id) DO UPDATE SET
                    wins = wins + excluded.wins,
                    losses = losses + excluded.losses,
                    total_attempts = total_attempts + excluded.total_attempts
                """,
                (chat_id, wins, losses, attempts),
            )

    def get_stats(self, chat_id: int) -> dict[str, int | float]:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT wins, losses, total_attempts FROM game_stats WHERE chat_id = ?",
                (chat_id,),
            ).fetchone()

        if row is None:
            return {"wins": 0, "losses": 0, "games": 0, "average_attempts": 0.0}

        wins, losses, total_attempts = row
        games = wins + losses
        return {
            "wins": wins,
            "losses": losses,
            "games": games,
            "average_attempts": total_attempts / games,
        }

    def get_top(self, limit: int = 10) -> list[dict[str, int | float | str]]:
        if limit < 1:
            raise ValueError("Лимит рейтинга должен быть положительным")

        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                  SELECT game_stats.chat_id,
                       COALESCE(players.display_name, 'Игрок ' || CAST(game_stats.chat_id AS TEXT)),
                      game_stats.wins, game_stats.losses, game_stats.total_attempts
                  FROM game_stats
                  LEFT JOIN players ON players.chat_id = game_stats.chat_id
                WHERE wins + losses > 0
                ORDER BY wins DESC, losses ASC, total_attempts ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {
                "chat_id": chat_id,
                "display_name": display_name,
                "wins": wins,
                "losses": losses,
                "games": wins + losses,
                "average_attempts": total_attempts / (wins + losses),
            }
            for chat_id, display_name, wins, losses, total_attempts in rows
        ]
