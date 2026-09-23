"""Local project tracking and lightweight skill assessment."""

from __future__ import annotations

import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class ProjectAssessment:
    category: str
    skills: tuple[str, ...]
    level: str


KEYWORDS: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("telegram", ("Python", "Telegram API", "SQLite"), "бот / интеграция"),
    ("бот", ("Python", "API", "автоматизация"), "бот / интеграция"),
    ("api", ("Python", "REST API", "интеграции"), "backend / API"),
    ("fastapi", ("Python", "FastAPI", "REST API"), "backend / API"),
    ("сайт", ("HTML/CSS", "веб-разработка"), "веб-проект"),
    ("frontend", ("JavaScript", "веб-разработка"), "веб-проект"),
    ("данн", ("Python", "работа с данными"), "данные / автоматизация"),
    ("автомат", ("Python", "автоматизация"), "данные / автоматизация"),
    ("тест", ("Python", "тестирование"), "качество / тесты"),
)


def assess_project(title: str, description: str) -> ProjectAssessment:
    text = f"{title} {description}".lower()
    matches = [entry for keyword, *entry in KEYWORDS if keyword in text]
    if not matches:
        return ProjectAssessment("проект разработки", ("Python", "декомпозиция задач"), "исследование")

    skills: list[str] = []
    categories: list[str] = []
    for skill_group, category in matches:
        categories.append(category)
        for skill in skill_group:
            if skill not in skills:
                skills.append(skill)
    level = "практика" if len(skills) < 3 else "портфолио"
    return ProjectAssessment(" + ".join(dict.fromkeys(categories)), tuple(skills), level)


class ProjectStorage:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self._create_table()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.database_path)

    def _create_table(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tracked_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    skills TEXT NOT NULL,
                    level TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'В работе',
                    project_path TEXT NOT NULL DEFAULT '',
                    started_at TEXT,
                    completed_at TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            columns = {row[1] for row in connection.execute("PRAGMA table_info(tracked_projects)")}
            for name, definition in (
                ("project_path", "TEXT NOT NULL DEFAULT ''"),
                ("started_at", "TEXT"),
                ("completed_at", "TEXT"),
            ):
                if name not in columns:
                    connection.execute(f"ALTER TABLE tracked_projects ADD COLUMN {name} {definition}")

    def add_project(self, title: str, description: str, project_path: str = "") -> int:
        title = title.strip()
        description = description.strip()
        if not title:
            raise ValueError("Название проекта не может быть пустым")
        assessment = assess_project(title, description)
        with closing(self._connect()) as connection, connection:
            cursor = connection.execute(
                """
                INSERT INTO tracked_projects (title, description, category, skills, level, project_path)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (title, description, assessment.category, json.dumps(assessment.skills), assessment.level, project_path.strip()),
            )
        return int(cursor.lastrowid)

    def list_projects(self) -> list[dict[str, object]]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                  SELECT id, title, description, category, skills, level, status,
                      project_path, started_at, completed_at, created_at
                FROM tracked_projects ORDER BY id DESC
                """
            ).fetchall()
        return [
            {
                "id": project_id,
                "title": title,
                "description": description,
                "category": category,
                "skills": tuple(json.loads(skills)),
                "level": level,
                "status": status,
                "project_path": project_path,
                "started_at": started_at,
                "completed_at": completed_at,
                "created_at": created_at,
            }
            for project_id, title, description, category, skills, level, status,
            project_path, started_at, completed_at, created_at in rows
        ]

    def complete_project(self, project_id: int) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """
                UPDATE tracked_projects
                SET status = 'Готово', completed_at = COALESCE(completed_at, ?)
                WHERE id = ?
                """,
                (datetime.now(timezone.utc).isoformat(), project_id),
            )

    def start_project(self, project_id: int) -> dict[str, object] | None:
        started_at = datetime.now(timezone.utc).isoformat()
        with closing(self._connect()) as connection, connection:
            connection.execute(
                "UPDATE tracked_projects SET status = 'В работе', started_at = ? WHERE id = ?",
                (started_at, project_id),
            )
        return next((project for project in self.list_projects() if project["id"] == project_id), None)

    def get_summary(self) -> dict[str, object]:
        projects = self.list_projects()
        skills = sorted({skill for project in projects for skill in project["skills"]})
        completed = sum(project["status"] == "Готово" for project in projects)
        return {"total": len(projects), "completed": completed, "skills": skills}