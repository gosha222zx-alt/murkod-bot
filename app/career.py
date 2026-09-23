"""Career guidance based on the user's verified project progress."""

from __future__ import annotations

from typing import TypedDict


class CareerSnapshot(TypedDict):
    completed_days: int
    total_days: int
    games: int
    wins: int
    losses: int


def build_market_response() -> str:
    return (
        "Муркод: направления, которые стоит проверить на спрос:\n\n"
        "1. Telegram-боты для малого бизнеса\n"
        "Что делать: FAQ, заявки, запись клиентов, уведомления.\n"
        "Портфолио: бот для салона или сервиса с SQLite и админ-командами.\n\n"
        "2. AI-помощники по документам\n"
        "Что делать: ответы по базе знаний, краткие выжимки, поиск по файлам.\n"
        "Портфолио: бот, который отвечает по загруженным инструкциям.\n\n"
        "3. Автоматизация процессов\n"
        "Что делать: отчёты, обработка таблиц, уведомления и перенос данных.\n"
        "Портфолио: ежедневный отчёт из CSV/Excel в Telegram.\n\n"
        "Проверка ниши: найди 10 свежих вакансий или заказов, выпиши повторяющиеся "
        "требования и выбери одну задачу для демо за 7 дней."
    )


def build_career_response(snapshot: CareerSnapshot) -> str:
    completed_days = snapshot["completed_days"]
    total_days = snapshot["total_days"]
    games = snapshot["games"]
    wins = snapshot["wins"]
    losses = snapshot["losses"]

    if completed_days >= 14 and games >= 5:
        level = "Уверенная учебная база, переход к первым коммерческим задачам"
        next_step = "Собери демо AI-бота для конкретного бизнеса и предложи его 3 потенциальным клиентам."
    elif completed_days >= 5 or games >= 3:
        level = "Рабочая база Python и первый проект для портфолио"
        next_step = "Добавь FastAPI или админ-панель и опиши проект как кейс в README."
    else:
        level = "Начало пути: базовые навыки уже превращаются в проект"
        next_step = "Продолжай учебный план и доведи Telegram-бота до законченного демо."

    return (
        "Мяу, это персональная оценка Муркода:\n\n"
        f"Уровень: {level}.\n"
        f"Учебные дни: {completed_days} из {total_days}.\n"
        f"Игры: {games}, победы: {wins}, поражения: {losses}.\n\n"
        "Подходящие ниши для проверки спроса:\n"
        "1. AI-боты для FAQ, заявок и записи клиентов.\n"
        "2. Python backend: FastAPI, PostgreSQL и REST API.\n"
        "3. Автоматизация отчётов, таблиц и уведомлений.\n\n"
        f"Ближайший шаг: {next_step}\n"
        "Проверь 10 свежих вакансий или заказов и выпиши повторяющиеся требования."
    )
