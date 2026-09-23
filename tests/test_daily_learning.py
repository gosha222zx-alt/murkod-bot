import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from daily_learning import (
    build_done_response,
    build_progress_response,
    build_today_response,
    get_day_number,
    get_today_lesson,
    load_plan,
)


class TestDailyLearning(unittest.TestCase):
    def setUp(self):
        self.plan = {
            "start_date": "2026-09-22",
            "daily_hours": 3,
            "days": [
                {"day": 1, "title": "Первый шаг", "tasks": ["Изучать"]},
                {"day": 2, "title": "Второй шаг", "tasks": ["Практиковаться"]},
            ],
        }

    def test_returns_lesson_for_date(self):
        lesson = get_today_lesson(self.plan, date(2026, 9, 23))
        self.assertEqual(lesson["title"], "Второй шаг")

    def test_returns_none_outside_plan(self):
        self.assertIsNone(get_today_lesson(self.plan, date(2026, 9, 21)))
        self.assertIsNone(get_today_lesson(self.plan, date(2026, 9, 24)))

    def test_load_plan_reads_json_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "plan.json"
            path.write_text(json.dumps(self.plan), encoding="utf-8")
            loaded = load_plan(path)
        self.assertEqual(loaded["daily_hours"], 3)
        self.assertEqual(len(loaded["days"]), 2)

    def test_build_today_response_contains_lesson(self):
        response = build_today_response(self.plan, date(2026, 9, 22))
        self.assertIn("День 1: Первый шаг", response)
        self.assertIn("План на 3 часа", response)

    def test_build_today_response_handles_dates_outside_plan(self):
        response = build_today_response(self.plan, date(2026, 9, 24))
        self.assertIn("урок не найден", response)

    def test_get_day_number(self):
        self.assertEqual(get_day_number(self.plan, date(2026, 9, 22)), 1)
        self.assertEqual(get_day_number(self.plan, date(2026, 9, 23)), 2)

    def test_build_done_response_distinguishes_first_and_repeated_completion(self):
        lesson = self.plan["days"][0]
        self.assertIn("отмечен как выполненный", build_done_response(1, lesson, False))
        self.assertIn("уже отмечен", build_done_response(1, lesson, True))

    def test_build_progress_response_counts_unique_plan_days(self):
        response = build_progress_response(self.plan, [1, 1, 2, 99])
        self.assertIn("Выполнено: 2 из 2 дней (100%)", response)
        self.assertIn("Выполненные дни: 1, 2, 99", response)


if __name__ == "__main__":
    unittest.main()
