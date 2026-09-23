"""Send the local progress report to Telegram once a week."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

from app.integrations import send_telegram_message
from app.project_tracker import ProjectStorage


def build_report(storage: ProjectStorage) -> str:
    summary = storage.get_summary()
    skills = ", ".join(summary["skills"]) or "пока не определены"
    return (
        "Муркод · недельный отчёт\n\n"
        f"Задач всего: {summary['total']}\n"
        f"Готово: {summary['completed']}\n"
        f"Навыки: {skills}\n\n"
        "Следующий шаг: выбери одну незавершённую задачу и доведи её до результата для портфолио."
    )


if __name__ == "__main__":
    load_dotenv()
    data_dir = Path(os.getenv("MURKOD_DATA_DIR", Path(__file__).parent))
    send_telegram_message(build_report(ProjectStorage(data_dir / "projects.sqlite3")))
