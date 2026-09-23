"""Helpers for connecting GuessGame to a Telegram handler."""

from __future__ import annotations

from app.guess_game import GuessGame


def parse_guess(text: str) -> int | None:
    """Return an integer guess or None when the message is not an integer."""
    try:
        return int(text.strip())
    except ValueError:
        return None


def build_game_response(result: str, game: GuessGame) -> str:
    """Turn a GuessGame result into a user-facing Telegram message."""
    if result == "win":
        return (
            f"Победа! Ты угадал число за {game.attempts} попыток.\n"
            "Запусти /guess, чтобы сыграть ещё раз."
        )
    if result == "lose":
        return (
            f"Попытки закончились. Загаданное число было {game.secret}.\n"
            "Запусти /guess, чтобы попробовать снова."
        )

    hint = "больше" if result == "higher" else "меньше"
    return f"Загаданное число {hint}. Осталось попыток: {game.remaining_attempts}."


def build_stats_response(stats: dict[str, int | float]) -> str:
    return (
        "Твоя статистика:\n"
        f"Игр: {stats['games']}\n"
        f"Побед: {stats['wins']}\n"
        f"Поражений: {stats['losses']}\n"
        f"Среднее число попыток: {stats['average_attempts']:.1f}"
    )


def build_top_response(players: list[dict[str, int | float | str]]) -> str:
    if not players:
        return "Рейтинг пока пуст. Сыграй первую игру через /guess."

    lines = ["Топ игроков:"]
    for position, player in enumerate(players, start=1):
        lines.append(
            f"{position}. {player['display_name']} — побед: {player['wins']}, "
            f"игр: {player['games']}, среднее попыток: "
            f"{player['average_attempts']:.1f}"
        )
    return "\n".join(lines)
