"""Optional AI, GitHub, Telegram, VS Code, and job-feed integrations."""

from __future__ import annotations

import json
import os
import subprocess
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from app.project_tracker import ProjectAssessment, assess_project


@dataclass(frozen=True)
class JobItem:
    title: str
    url: str
    source: str
    summary: str


def open_in_vscode(project_path: str) -> None:
    path = Path(project_path).expanduser() if project_path.strip() else Path.cwd()
    path.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.Popen(["code", str(path)], shell=False)
    except (FileNotFoundError, OSError):
        os.startfile(path)  # type: ignore[attr-defined]


def assess_with_ai(title: str, description: str) -> tuple[ProjectAssessment, str]:
    """Use Groq when configured, with a deterministic local fallback."""
    assessment = assess_project(title, description)
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return assessment, "Локальная оценка сохранена. Для подробного AI-разбора задай GROQ_API_KEY."
    try:
        from groq import Groq

        response = Groq(api_key=api_key).chat.completions.create(
            model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
            messages=[
                {"role": "system", "content": "Кратко оцени задачу программиста: тип, навыки, следующий шаг и результат для портфолио. Отвечай по-русски."},
                {"role": "user", "content": f"Название: {title}\nОписание: {description}"},
            ],
        )
        return assessment, response.choices[0].message.content or "AI не вернул пояснение."
    except Exception as error:
        return assessment, f"AI временно недоступен ({error.__class__.__name__}). Локальная оценка сохранена."


def send_telegram_message(text: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        raise RuntimeError("Задай TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID в .env")
    payload = urllib.parse.urlencode({"chat_id": chat_id, "text": text}).encode()
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage", data=payload, method="POST"
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        if response.status != 200:
            raise RuntimeError(f"Telegram API вернул HTTP {response.status}")


def github_repositories() -> list[dict[str, str]]:
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Задай GITHUB_TOKEN в .env")
    request = urllib.request.Request(
        "https://api.github.com/user/repos?sort=updated&per_page=30",
        headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        return [
            {"name": item["name"], "url": item["html_url"], "language": item.get("language") or ""}
            for item in json.loads(response.read())
        ]


def load_job_items() -> list[JobItem]:
    """Read configured RSS/Atom feeds for manual review only."""
    feed_urls = [url.strip() for url in os.getenv("JOB_FEEDS", "").split(",") if url.strip()]
    items: list[JobItem] = []
    for feed_url in feed_urls:
        try:
            request = urllib.request.Request(feed_url, headers={"User-Agent": "MurkodWidget/1.0"})
            with urllib.request.urlopen(request, timeout=10) as response:
                root = ET.fromstring(response.read())
            source = urllib.parse.urlparse(feed_url).netloc
            entries = root.findall(".//item") + root.findall(".//{http://www.w3.org/2005/Atom}entry")
            for entry in entries:
                title = entry.findtext("title") or "Без названия"
                link = entry.findtext("link") or ""
                summary = entry.findtext("description") or entry.findtext("summary") or ""
                items.append(JobItem(title.strip(), link.strip(), source, summary.strip()))
        except (OSError, ET.ParseError, ValueError):
            continue
    return items[:30]
