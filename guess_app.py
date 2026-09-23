import tkinter as tk
from tkinter import messagebox

from app.guess_game import GuessGame, MAX_ATTEMPTS, MAX_NUMBER, MIN_NUMBER


WINDOW_BG = "#07111f"
PANEL_BG = "#0d1d2e"
TEXT = "#e9fff4"
MUTED = "#83a99b"
GREEN = "#48f58a"
CYAN = "#65e6ff"
RED = "#ff6b7d"


class GuessApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Угадай число // MATRIX")
        self.root.geometry("620x700")
        self.root.minsize(520, 620)
        self.root.configure(bg=WINDOW_BG)

        self.game = GuessGame()
        self.matrix_columns: list[dict[str, object]] = []
        self.matrix_items: list[int] = []
        self._build_ui()
        self._setup_matrix()
        self._matrix_tick()

    def _build_ui(self) -> None:
        self.canvas = tk.Canvas(self.root, bg=WINDOW_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        content = tk.Frame(self.canvas, bg=PANEL_BG, padx=42, pady=34)
        self.canvas.create_window(0, 0, anchor="nw", window=content, tags="content")
        content.bind("<Configure>", self._resize_content)

        tk.Label(
            content,
            text="УГАДАЙ ЧИСЛО",
            font=("Consolas", 28, "bold"),
            bg=PANEL_BG,
            fg=GREEN,
        ).pack(pady=(0, 6))
        tk.Label(
            content,
            text="СИСТЕМА ЗАГАДАЛА ЧИСЛО ОТ 1 ДО 100",
            font=("Consolas", 10),
            bg=PANEL_BG,
            fg=MUTED,
        ).pack()

        self.status = tk.Label(
            content,
            text="У тебя 4 попытки. Введи число:",
            font=("Segoe UI", 14),
            bg=PANEL_BG,
            fg=TEXT,
            wraplength=450,
            justify="center",
        )
        self.status.pack(pady=(34, 20))

        self.entry = tk.Entry(
            content,
            font=("Consolas", 26, "bold"),
            width=7,
            justify="center",
            bg="#102b3b",
            fg=TEXT,
            insertbackground=GREEN,
            relief="flat",
        )
        self.entry.pack(ipady=8)
        self.entry.bind("<Return>", lambda _event: self.make_guess())
        self.entry.focus_set()

        self.attempts_label = tk.Label(
            content,
            text="Попытка 1 из 4",
            font=("Consolas", 11),
            bg=PANEL_BG,
            fg=CYAN,
        )
        self.attempts_label.pack(pady=(14, 22))

        self.guess_button = tk.Button(
            content,
            text="ПРОВЕРИТЬ",
            command=self.make_guess,
            font=("Consolas", 12, "bold"),
            bg=GREEN,
            fg="#04110a",
            activebackground="#a4ffc4",
            relief="flat",
            cursor="hand2",
            padx=28,
            pady=10,
        )
        self.guess_button.pack()

        self.new_game_button = tk.Button(
            content,
            text="НОВАЯ ИГРА",
            command=self.new_game,
            font=("Consolas", 10),
            bg="#173347",
            fg=TEXT,
            activebackground="#24516a",
            activeforeground=TEXT,
            relief="flat",
            cursor="hand2",
            padx=20,
            pady=8,
        )
        self.new_game_button.pack(pady=(14, 0))

    def _resize_content(self, _event: tk.Event) -> None:
        self.canvas.itemconfigure("content", width=self.canvas.winfo_width())

    def _setup_matrix(self) -> None:
        self.root.update_idletasks()
        width = max(self.root.winfo_width(), 520)
        self.matrix_columns = [
            {"x": x, "y": -((x * 17) % 300), "speed": 2 + (x % 4), "length": 5 + (x % 6)}
            for x in range(8, width, 22)
        ]

    def _matrix_tick(self) -> None:
        for item in self.matrix_items:
            self.canvas.delete(item)
        self.matrix_items.clear()
        for column in self.matrix_columns:
            column["y"] = int(column["y"]) + int(column["speed"])
            if int(column["y"]) > self.root.winfo_height() + 100:
                column["y"] = -80
            for offset in range(int(column["length"])):
                y = int(column["y"]) - offset * 18
                if y > 0:
                    item = self.canvas.create_text(
                        int(column["x"]), y, text=str((int(column["x"]) + y) % 10),
                        fill="#164d42" if offset else GREEN, font=("Consolas", 12),
                    )
                    self.matrix_items.append(item)
        self.root.after(80, self._matrix_tick)

    def make_guess(self) -> None:
        try:
            value = int(self.entry.get().strip())
        except ValueError:
            self.status.config(text="Введи целое число от 1 до 100", fg=RED)
            return

        try:
            result = self.game.guess(value)
        except ValueError as error:
            self.status.config(text=str(error), fg=RED)
            return

        self.entry.delete(0, tk.END)
        self.attempts_label.config(text=f"Попытка {self.game.attempts + 1} из {MAX_ATTEMPTS}")
        if result == "win":
            self.status.config(text="ПОЗДРАВЛЯЮ, КОЖАНЫЙ МЕШОК!", fg=GREEN)
            self._finish_round()
        elif result == "lose":
            self.status.config(
                text=f"Ну ничего страшного, все равно искусственный интеллект вас пробатит.\nЧисло было: {self.game.secret}",
                fg=RED,
            )
            self._finish_round()
        else:
            direction = "больше" if result == "higher" else "меньше"
            self.status.config(text=f"Попробуй еще раз. Нужно число {direction}.", fg=TEXT)
            self.attempts_label.config(text=f"Попытка {self.game.attempts + 1} из {MAX_ATTEMPTS}")

    def _finish_round(self) -> None:
        self.guess_button.config(state=tk.DISABLED)
        self.entry.config(state=tk.DISABLED)

    def new_game(self) -> None:
        self.game = GuessGame()
        self.status.config(text="У тебя 4 попытки. Введи число:", fg=TEXT)
        self.attempts_label.config(text="Попытка 1 из 4")
        self.guess_button.config(state=tk.NORMAL)
        self.entry.config(state=tk.NORMAL)
        self.entry.delete(0, tk.END)
        self.entry.focus_set()


if __name__ == "__main__":
    window = tk.Tk()
    GuessApp(window)
    window.mainloop()