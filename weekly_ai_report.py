"""Еженедельный ИИ-анализ прогресса через Groq."""
import os
from datetime import datetime, timedelta
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

from app.integrations import send_telegram_message
from app.project_tracker import ProjectStorage

load_dotenv()

DATA_DIR = Path(os.getenv("MURKOD_DATA_DIR", Path(__file__).parent))
STORAGE = ProjectStorage(DATA_DIR / "projects.sqlite3")

SYSTEM_PROMPT = (
    "Ты — Муркод, кот-наставник по программированию. Ты анализируешь "
    "прогресс ученика за неделю и даёшь конкретные советы. Говори коротко, "
    "по делу, без воды. Будь честным, но поддерживающим. Отвечай по-русски."
)


def build_context() -> str:
    """Собирает текстовый контекст о проектах для отправки в Groq."""
    projects = STORAGE.list_projects()
    summary = STORAGE.get_summary()
    week_ago = datetime.now() - timedelta(days=7)

    recent_new = []
    recent_done = []
    for p in projects:
        try:
            created = datetime.fromisoformat(p.get("created_at") or "")
            if created >= week_ago:
                recent_new.append(p)
        except (ValueError, TypeError):
            pass
        if p["status"] == "Готово" and p.get("completed_at"):
            try:
                done = datetime.fromisoformat(p["completed_at"])
                if done >= week_ago:
                    recent_done.append(p)
            except (ValueError, TypeError):
                pass

    lines = [
        f"Всего проектов: {summary['total']}",
        f"Готово всего: {summary['completed']}",
        f"Новых за неделю: {len(recent_new)}",
        f"Завершено за неделю: {len(recent_done)}",
        f"Навыки: {', '.join(summary['skills']) or 'нет'}",
        "",
        "Проекты за неделю:",
    ]
    for p in recent_new:
        lines.append(f"• [НОВЫЙ] {p['title']} — {p['status']}")
    for p in recent_done:
        lines.append(f"• [ГОТОВО] {p['title']}")

    if not recent_new and not recent_done:
        lines.append("(за неделю ничего не менялось)")

    return "\n".join(lines)


def ask_groq(context: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY не задан в .env")

    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Вот статистика за неделю:\n\n"
                    f"{context}\n\n"
                    "Напиши короткий разбор: что получилось, что улучшить, "
                    "какой следующий шаг. Максимум 5 предложений."
                ),
            },
        ],
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content or "AI не дал ответ."


def main() -> None:
    context = build_context()
    ai_analysis = ask_groq(context)

    report = (
        "📊 <b>Муркод: отчёт за неделю</b>\n\n"
        f"<pre>{context}</pre>\n\n"
        f"<b>🤖 Анализ:</b>\n{ai_analysis}"
    )

    send_telegram_message(report)
    print("Отчёт отправлен.")


if __name__ == "__main__":
    main()