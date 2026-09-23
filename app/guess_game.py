import random


MAX_ATTEMPTS = 4
MIN_NUMBER = 1
MAX_NUMBER = 100


class GuessGame:
    """Stores the state and rules for one number-guessing round."""

    def __init__(self, secret: int | None = None) -> None:
        self.secret = secret if secret is not None else random.randint(MIN_NUMBER, MAX_NUMBER)
        self.attempts = 0
        self.guesses: list[int] = []
        self.finished = False

    @property
    def remaining_attempts(self) -> int:
        return MAX_ATTEMPTS - self.attempts

    def reset(self) -> None:
        self.attempts = 0
        self.guesses = []
        self.finished = False

    def guess(self, value: int) -> str:
        if self.finished:
            raise RuntimeError("Игра уже закончена")
        if not MIN_NUMBER <= value <= MAX_NUMBER:
            raise ValueError("Число должно быть от 1 до 100")

        self.attempts += 1
        self.guesses.append(value)
        if value == self.secret:
            self.finished = True
            return "win"
        if self.attempts >= MAX_ATTEMPTS:
            self.finished = True
            return "lose"
        return "higher" if value < self.secret else "lower"