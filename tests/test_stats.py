import tempfile
import unittest
from pathlib import Path

from app.game_storage import GameStorage
from app.guess_bot import build_stats_response


class TestStats(unittest.TestCase):
    def test_new_player_has_empty_stats(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = GameStorage(Path(directory) / "games.sqlite3")
            stats = storage.get_stats(123)

        self.assertEqual(stats["games"], 0)
        self.assertEqual(stats["wins"], 0)
        self.assertEqual(stats["losses"], 0)
        self.assertEqual(stats["average_attempts"], 0.0)

    def test_records_results_and_calculates_average(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = GameStorage(Path(directory) / "games.sqlite3")
            storage.record_result(123, "win", 2)
            storage.record_result(123, "win", 1)
            storage.record_result(123, "lose", 4)
            stats = storage.get_stats(123)

        self.assertEqual(stats["games"], 3)
        self.assertEqual(stats["wins"], 2)
        self.assertEqual(stats["losses"], 1)
        self.assertAlmostEqual(stats["average_attempts"], 7 / 3)

    def test_stats_response_contains_values(self):
        response = build_stats_response(
            {"games": 3, "wins": 2, "losses": 1, "average_attempts": 2.333}
        )

        self.assertIn("Игр: 3", response)
        self.assertIn("Побед: 2", response)
        self.assertIn("Среднее число попыток: 2.3", response)


if __name__ == "__main__":
    unittest.main()
