import tempfile
import unittest
from pathlib import Path

from app.project_tracker import ProjectStorage, assess_project


class TestProjectTracker(unittest.TestCase):
    def test_assessment_detects_project_skills(self):
        assessment = assess_project("Бот", "Telegram API и SQLite для заявок")

        self.assertIn("бот / интеграция", assessment.category)
        self.assertIn("Telegram API", assessment.skills)
        self.assertIn("SQLite", assessment.skills)

    def test_storage_tracks_completion_and_summary(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = ProjectStorage(Path(directory) / "projects.sqlite3")
            project_id = storage.add_project("Тест API", "FastAPI сервис")
            storage.complete_project(project_id)

            summary = storage.get_summary()

        self.assertEqual(summary["total"], 1)
        self.assertEqual(summary["completed"], 1)
        self.assertIn("FastAPI", summary["skills"])


if __name__ == "__main__":
    unittest.main()