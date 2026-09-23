import tempfile
import unittest
from pathlib import Path

from app.game_storage import GameStorage
from app.guess_game import GuessGame


class TestGameStorage(unittest.TestCase):
    def test_save_and_load_preserves_game_state(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = GameStorage(Path(directory) / "games.sqlite3")
            game = GuessGame(secret=73)
            game.guess(20)
            game.guess(80)
            storage.save(123, game)

            restored = storage.load_all()[123]

        self.assertEqual(restored.secret, 73)
        self.assertEqual(restored.attempts, 2)
        self.assertEqual(restored.guesses, [20, 80])
        self.assertFalse(restored.finished)
        self.assertEqual(restored.remaining_attempts, 2)

    def test_save_updates_existing_chat(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = GameStorage(Path(directory) / "games.sqlite3")
            game = GuessGame(secret=50)
            storage.save(123, game)
            game.guess(20)
            storage.save(123, game)

            games = storage.load_all()

        self.assertEqual(len(games), 1)
        self.assertEqual(games[123].attempts, 1)
        self.assertEqual(games[123].guesses, [20])

    def test_learning_day_is_saved_only_once(self):
        with tempfile.TemporaryDirectory() as directory:
            storage = GameStorage(Path(directory) / "games.sqlite3")
            first_mark = storage.mark_learning_day(123, 1)
            second_mark = storage.mark_learning_day(123, 1)
            storage.mark_learning_day(123, 3)

            completed_days = storage.get_completed_learning_days(123)

        self.assertTrue(first_mark)
        self.assertFalse(second_mark)
        self.assertEqual(completed_days, [1, 3])


if __name__ == "__main__":
    unittest.main()
