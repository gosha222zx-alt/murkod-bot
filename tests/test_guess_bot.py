import unittest

from app.guess_bot import build_game_response, parse_guess
from app.guess_game import GuessGame


class TestGuessBot(unittest.TestCase):
    def test_parse_guess_accepts_integer_text(self):
        self.assertEqual(parse_guess(" 42 "), 42)
        self.assertEqual(parse_guess("-3"), -3)

    def test_parse_guess_rejects_non_integer_text(self):
        self.assertIsNone(parse_guess("сорок два"))
        self.assertIsNone(parse_guess(""))

    def test_build_game_response_for_hint(self):
        game = GuessGame(secret=50)
        result = game.guess(20)

        response = build_game_response(result, game)

        self.assertIn("больше", response)
        self.assertIn("Осталось попыток: 3", response)

    def test_build_game_response_for_win(self):
        game = GuessGame(secret=50)
        result = game.guess(50)

        response = build_game_response(result, game)

        self.assertIn("Победа", response)
        self.assertIn("/guess", response)

    def test_build_game_response_for_loss(self):
        game = GuessGame(secret=50)
        for _ in range(4):
            result = game.guess(20)

        response = build_game_response(result, game)

        self.assertIn("закончились", response)
        self.assertIn("50", response)


if __name__ == "__main__":
    unittest.main()
