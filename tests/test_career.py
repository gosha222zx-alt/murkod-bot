import unittest

from app.career import build_career_response, build_market_response


class TestCareer(unittest.TestCase):
    def test_beginner_gets_realistic_next_step(self):
        response = build_career_response(
            {"completed_days": 0, "total_days": 30, "games": 0, "wins": 0, "losses": 0}
        )
        self.assertIn("Начало пути", response)
        self.assertIn("Продолжай учебный план", response)

    def test_progress_changes_career_recommendation(self):
        response = build_career_response(
            {"completed_days": 15, "total_days": 30, "games": 6, "wins": 4, "losses": 2}
        )
        self.assertIn("переход к первым коммерческим задачам", response)
        self.assertIn("3 потенциальным клиентам", response)

    def test_response_lists_market_niches(self):
        response = build_career_response(
            {"completed_days": 5, "total_days": 30, "games": 1, "wins": 1, "losses": 0}
        )
        self.assertIn("AI-боты", response)
        self.assertIn("FastAPI", response)
        self.assertIn("Автоматизация", response)

    def test_market_response_contains_actionable_projects(self):
        response = build_market_response()
        self.assertIn("Telegram-боты", response)
        self.assertIn("базе знаний", response)
        self.assertIn("CSV/Excel", response)
        self.assertIn("за 7 дней", response)


if __name__ == "__main__":
    unittest.main()
