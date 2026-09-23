import unittest

from app.guess_game import GuessGame, MAX_ATTEMPTS


class TestGuessGame(unittest.TestCase):
    def test_hints_and_win(self):
        game = GuessGame(secret=50)
        self.assertEqual(game.guess(20), "higher")
        self.assertEqual(game.guess(80), "lower")
        self.assertEqual(game.guess(50), "win")
        self.assertTrue(game.finished)

    def test_fourth_wrong_attempt_loses(self):
        game = GuessGame(secret=50)
        for _ in range(MAX_ATTEMPTS - 1):
            self.assertEqual(game.guess(20), "higher")
        self.assertEqual(game.guess(20), "lose")
        self.assertTrue(game.finished)

    def test_invalid_values_do_not_use_attempt(self):
        game = GuessGame(secret=50)
        with self.assertRaises(ValueError):
            game.guess(101)
        self.assertEqual(game.attempts, 0)

    def test_tracks_guesses_and_remaining_attempts(self):
        game = GuessGame(secret=50)

        self.assertEqual(game.remaining_attempts, MAX_ATTEMPTS)
        game.guess(20)
        game.guess(80)

        self.assertEqual(game.guesses, [20, 80])
        self.assertEqual(game.remaining_attempts, MAX_ATTEMPTS - 2)

    def test_reset_starts_game_again(self):
        game = GuessGame(secret=50)
        game.guess(20)
        game.reset()

        self.assertEqual(game.attempts, 0)
        self.assertEqual(game.guesses, [])
        self.assertFalse(game.finished)


if __name__ == "__main__":
    unittest.main()