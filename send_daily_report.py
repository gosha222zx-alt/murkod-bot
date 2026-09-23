"""Отправляет ежедневный отчёт в Telegram."""
import os
from pathlib import Path

from dotenv import load_dotenv

from app.integrations import send_telegram_message
from app.project_tracker import ProjectStorage
from weekly_report import build_report

load_dotenv()

DATA_DIR = Path(os.getenv("MURKOD_DATA_DIR", Path(__file__).parent))
STORAGE = ProjectStorage(DATA_DIR / "projects.sqlite3")


def main() -> None:
    report = build_report(STORAGE)
    send_telegram_message(report)
    print("Отчёт отправлен.")


if __name__ == "__main__":
    main()