import unittest

from app.logic import build_report, greet_user


class TestLogic(unittest.TestCase):
    def test_greet_user(self):
        self.assertEqual(
            greet_user("Анна"),
            "Привет, Анна! Это базовый проект на Python.",
        )

    def test_build_report(self):
        data = build_report(["a", "b", "c"])
        self.assertEqual(data["count"], 3)
        self.assertEqual(data["items"], ["a", "b", "c"])


if __name__ == "__main__":
    unittest.main()
