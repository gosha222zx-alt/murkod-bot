import tempfile
import unittest
from pathlib import Path

from app.game_storage import GameStorage
from app.guess_bot import build_top_response


class TestLeaderboard(unittest.TestCase):
    def test_top_orders_players_by_wins_then_attempts(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = GameStorage(Path(directory) / "games.sqlite3")
            storage.save_player(100, "Анна")
            storage.record_result(100, "win", 4)
            storage.record_result(100, "win", 3)
            storage.record_result(200, "win", 1)
            storage.record_result(200, "lose", 4)
            storage.record_result(300, "win", 2)
            top = storage.get_top(limit=3)

        self.assertEqual([player["display_name"] for player in top], ["Анна", "Игрок 300", "Игрок 200"])
        self.assertEqual(top[0]["wins"], 2)
        self.assertAlmostEqual(top[1]["average_attempts"], 2.0)

    def test_empty_top_has_helpful_message(self):
        self.assertIn("Рейтинг пока пуст", build_top_response([]))

    def test_top_response_contains_player_data(self):
        response = build_top_response(
            [{"display_name": "Анна", "wins": 2, "games": 3, "average_attempts": 2.3}]
        )

        self.assertIn("1. Анна", response)
        self.assertIn("побед: 2", response)
        self.assertIn("среднее попыток: 2.3", response)


if __name__ == "__main__":
    unittest.main()
