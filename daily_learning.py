"""Показывает учебную задачу текущего дня при запуске Windows."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any


PLAN_FILE = Path(__file__).with_name("learning_plan.json")


def load_plan(path: Path = PLAN_FILE) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def get_day_number(plan: dict[str, Any], today: date) -> int:
    start_date = date.fromisoformat(plan["start_date"])
    return (today - start_date).days + 1


def get_today_lesson(plan: dict[str, Any], today: date) -> dict[str, Any] | None:
    day_number = get_day_number(plan, today)
    if day_number < 1 or day_number > len(plan["days"]):
        return None
    return plan["days"][day_number - 1]


def build_message(plan: dict[str, Any], lesson: dict[str, Any], today: date) -> str:
    start_date = date.fromisoformat(plan["start_date"])
    day_number = (today - start_date).days + 1
    tasks = "\n".join(f"- {task}" for task in lesson["tasks"])
    return (
        f"День {day_number}: {lesson['title']}\n\n"
        f"План на {plan['daily_hours']} часа:\n{tasks}\n\n"
        "Главное правило: в конце оставь заметку о том, чему научился."
    )


def build_today_response(plan: dict[str, Any], today: date) -> str:
    lesson = get_today_lesson(plan, today)
    if lesson is None:
        return (
            "На сегодня урок не найден: 30-дневный план ещё не начался "
            "или уже завершён."
        )
    return build_message(plan, lesson, today)


def build_done_response(day_number: int, lesson: dict[str, Any], already_done: bool) -> str:
    if already_done:
        return f"День {day_number} уже отмечен как выполненный: {lesson['title']}."
    return f"Готово! День {day_number} отмечен как выполненный: {lesson['title']}."


def build_progress_response(plan: dict[str, Any], completed_days: list[int]) -> str:
    total_days = len(plan["days"])
    unique_days = sorted(set(completed_days))
    completed_count = len([day for day in unique_days if 1 <= day <= total_days])
    percentage = completed_count / total_days * 100 if total_days else 0
    completed_text = ", ".join(str(day) for day in unique_days) or "пока нет"
    return (
        "Прогресс обучения:\n"
        f"Выполнено: {completed_count} из {total_days} дней ({percentage:.0f}%)\n"
        f"Выполненные дни: {completed_text}"
    )


def show_today_lesson() -> None:
    import tkinter as tk
    from tkinter import messagebox

    plan = load_plan()
    today = date.today()
    message = build_today_response(plan, today)

    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Твой шаг по Python", message)
    root.destroy()
