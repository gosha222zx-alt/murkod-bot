import sys
import random
import tkinter as tk
from pathlib import Path
import resource

class GuessGame:
    AI_PHRASES = [
        "Ха-ха! Система снова сильнее человека.",
        "Интересная попытка, но неправильная.",
        "Даже калькулятор справился бы лучше.",
        "ИИ записал это как очередной промах.",
        "Попробуй думать ещё раз.",
        "Мои нейроны сейчас тихо смеются.",
        "Почти! Но только в другой вселенной.",
        "Это число было далеко от истины.",
        "Человек, соберись!",
        "Система не впечатлена.",
        "Ещё одна попытка мимо цели.",
        "Может, попросить подсказку у калькулятора?",
        "Логика временно недоступна?",
        "Число выбрано смело, но неверно.",
        "ИИ уже начинает волноваться за тебя.",
        "Промах зафиксирован и сохранён.",
        "Шансы уменьшаются.",
        "Это была разминка? Надеюсь.",
        "Компьютер улыбается в цифровом формате.",
        "Не сдавайся, кожаный мешок!",
    ]

    LEVELS = {
        "Лёгкий": 12,
        "Средний": 8,
        "Ветеран": 5,
    }

    SPEEDS = {
        "Медленно": 500,
        "Обычно": 180,
        "Быстро": 70,
    }

    RAINBOW_COLORS = [
        "#ffadad",
        "#ffd6a5",
        "#fdffb6",
        "#caffbf",
        "#9bf6ff",
        "#bdb2ff",
        "#ffc6ff",
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Издёвка ИИ")
        self.root.geometry("820x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#080b18")

        self.level = "Лёгкий"
        self.max_attempts = self.LEVELS[self.level]
        self.button_speed = self.SPEEDS["Обычно"]

        self.secret = random.randint(1, 100)
        self.attempts = 0
        self.ai_phrases = []
        self.animation_job = None
        self.escape_job = None
        self.rainbow_index = 0

        self.canvas = tk.Canvas(
            root,
            width=820,
            height=520,
            bg="#080b18",
            highlightthickness=0,
        )
        self.canvas.place(x=0, y=0)

        self.settings_button = tk.Button(
            root,
            text="⚙ Настройки",
            command=self.open_settings,
            font=("Segoe UI", 9),
            bg="#252344",
            fg="#e8ecff",
            activebackground="#393267",
            relief="flat",
            cursor="hand2",
        )
        self.settings_button.place(x=705, y=5)

        self.main = tk.Frame(
            root,
            bg="#12182b",
            highlightbackground="#62e6ff",
            highlightthickness=1,
        )
        self.main.place(x=25, y=25, width=465, height=470)

        self.history_panel = tk.Frame(
            root,
            bg="#12182b",
            highlightbackground="#3d4675",
            highlightthickness=1,
        )
        self.history_panel.place(x=515, y=25, width=280, height=470)

        tk.Label(
            self.main,
            text="ИЗДЁВКА ИИ",
            font=("Segoe UI", 27, "bold"),
            fg="#62e6ff",
            bg="#12182b",
        ).pack(pady=(28, 8))

        tk.Label(
            self.main,
            text="Угадай число от 1 до 100",
            font=("Segoe UI", 14),
            fg="#e8ecff",
            bg="#12182b",
        ).pack()

        self.info = tk.Label(
            self.main,
            text="",
            font=("Segoe UI", 11),
            fg="#9ba8d1",
            bg="#12182b",
        )
        self.info.pack(pady=(8, 15))

        self.entry = tk.Entry(
            self.main,
            font=("Segoe UI", 20, "bold"),
            justify="center",
            width=10,
            bg="#0d1224",
            fg="#62e6ff",
            insertbackground="#62e6ff",
            relief="flat",
        )
        self.entry.pack(ipady=7)
        self.entry.focus()

        self.button = tk.Button(
            root,
            text="ПРОВЕРИТЬ",
            command=self.check_guess,
            font=("Segoe UI", 8, "bold"),
            bg="#695cff",
            fg="white",
            activebackground="#62e6ff",
            activeforeground="#080b18",
            relief="flat",
            width=11,
            height=1,
            cursor="hand2",
        )
        self.button.place(x=190, y=220)
        self.button.bind("<Enter>", self.schedule_button_escape)
        self.button.bind("<Leave>", self.cancel_button_escape)

        self.result = tk.Label(
            self.main,
            text="",
            font=("Segoe UI", 12),
            fg="#b8c2df",
            bg="#12182b",
            wraplength=420,
        )
        self.result.pack(pady=(38, 3))

        self.restart = tk.Button(
            self.main,
            text="НОВАЯ ИГРА",
            command=self.new_game,
            font=("Segoe UI", 11, "bold"),
            bg="#252344",
            fg="#c9c4ff",
            activebackground="#393267",
            relief="flat",
            width=18,
            cursor="hand2",
        )
        self.restart.pack(pady=18, ipady=5)

        tk.Label(
            self.history_panel,
            text="ИСТОРИЯ ЧИСЕЛ",
            font=("Segoe UI", 16, "bold"),
            fg="#62e6ff",
            bg="#12182b",
        ).pack(pady=(22, 5))

        tk.Label(
            self.history_panel,
            text="Твои предыдущие варианты:",
            font=("Segoe UI", 10),
            fg="#9ba8d1",
            bg="#12182b",
        ).pack(pady=(0, 12))

        history_frame = tk.Frame(
            self.history_panel,
            bg="#12182b",
        )
        history_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 18),
        )

        scrollbar = tk.Scrollbar(history_frame)
        scrollbar.pack(side="right", fill="y")

        self.history = tk.Listbox(
            history_frame,
            font=("Cascadia Code", 11),
            bg="#0d1224",
            fg="#c9c4ff",
            selectbackground="#3d4675",
            selectforeground="white",
            relief="flat",
            borderwidth=0,
            yscrollcommand=scrollbar.set,
            activestyle="none",
        )
        self.history.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.history.yview)

        self.reset_phrases()
        self.update_labels()
        self.root.bind("<Return>", lambda event: self.check_guess())

    def update_labels(self):
        self.info.config(
            text=(
                f"Уровень: {self.level} — "
                f"попыток: {self.max_attempts}"
            )
        )
        self.result.config(
            text=(
                "Попыток использовано: "
                f"0 из {self.max_attempts}"
            ),
            font=("Segoe UI", 12),
            fg="#b8c2df",
        )

    def reset_phrases(self):
        self.ai_phrases = self.AI_PHRASES.copy()
        random.shuffle(self.ai_phrases)

    def get_ai_phrase(self):
        if not self.ai_phrases:
            self.reset_phrases()
        return self.ai_phrases.pop()

    def open_settings(self):
        window = tk.Toplevel(self.root)
        window.title("Настройки")
        window.geometry("340x330")
        window.resizable(False, False)
        window.configure(bg="#12182b")
        window.transient(self.root)
        window.grab_set()

        tk.Label(
            window,
            text="НАСТРОЙКИ ИГРЫ",
            font=("Segoe UI", 16, "bold"),
            fg="#62e6ff",
            bg="#12182b",
        ).pack(pady=15)

        tk.Label(
            window,
            text="Уровень сложности:",
            font=("Segoe UI", 10),
            fg="#e8ecff",
            bg="#12182b",
        ).pack()

        level_var = tk.StringVar(value=self.level)

        level_menu = tk.OptionMenu(
            window,
            level_var,
            *self.LEVELS.keys(),
        )
        level_menu.config(
            bg="#695cff",
            fg="white",
            activebackground="#62e6ff",
            width=16,
        )
        level_menu.pack(pady=8)

        tk.Label(
            window,
            text="Скорость кнопки:",
            font=("Segoe UI", 10),
            fg="#e8ecff",
            bg="#12182b",
        ).pack()

        current_speed = next(
            name
            for name, value in self.SPEEDS.items()
            if value == self.button_speed
        )
        speed_var = tk.StringVar(value=current_speed)

        speed_menu = tk.OptionMenu(
            window,
            speed_var,
            *self.SPEEDS.keys(),
        )
        speed_menu.config(
            bg="#695cff",
            fg="white",
            activebackground="#62e6ff",
            width=16,
        )
        speed_menu.pack(pady=8)

        tk.Label(
            window,
            text="Медленно — 500 мс | Быстро — 70 мс",
            font=("Segoe UI", 9),
            fg="#9ba8d1",
            bg="#12182b",
        ).pack(pady=4)

        def apply_settings():
            self.level = level_var.get()
            self.max_attempts = self.LEVELS[self.level]
            self.button_speed = self.SPEEDS[speed_var.get()]
            window.destroy()
            self.new_game()

        tk.Button(
            window,
            text="ПРИМЕНИТЬ",
            command=apply_settings,
            font=("Segoe UI", 10, "bold"),
            bg="#62e6ff",
            fg="#080b18",
            activebackground="#ffffff",
            relief="flat",
            width=18,
        ).pack(pady=18)

    def schedule_button_escape(self, event=None):
        if self.button["state"] == "disabled":
            return

        if self.escape_job is not None:
            self.root.after_cancel(self.escape_job)

        self.escape_job = self.root.after(
            self.button_speed,
            self.move_button,
        )

    def cancel_button_escape(self, event=None):
        if self.escape_job is not None:
            self.root.after_cancel(self.escape_job)
            self.escape_job = None

    def move_button(self):
        self.escape_job = None
        self.root.update_idletasks()

        width = self.button.winfo_width()
        height = self.button.winfo_height()
        max_x = max(10, self.root.winfo_width() - width - 10)
        max_y = max(10, self.root.winfo_height() - height - 10)

        color = self.RAINBOW_COLORS[self.rainbow_index]
        self.rainbow_index = (
            self.rainbow_index + 1
        ) % len(self.RAINBOW_COLORS)

        self.button.config(
            bg=color,
            activebackground=color,
            fg="#202034",
        )

        self.button.place(
            x=random.randint(10, max_x),
            y=random.randint(10, max_y),
        )

    def check_guess(self):
        if self.attempts >= self.max_attempts:
            return

        try:
            guess = int(self.entry.get())
        except ValueError:
            self.result.config(
                text="Введи целое число от 1 до 100",
                fg="#ff6b9d",
            )
            return

        if not 1 <= guess <= 100:
            self.result.config(
                text="Число должно быть от 1 до 100",
                fg="#ff6b9d",
            )
            return

        self.attempts += 1
        self.entry.delete(0, tk.END)

        if guess == self.secret:
            self.history.insert(
                tk.END,
                f"{self.attempts:02}. {guess} — УГАДАЛ!",
            )
            self.history.see(tk.END)
            self.win()
            return

        phrase = self.get_ai_phrase()
        show_hint = random.choice([True, False])
        hint = "больше ↑" if guess < self.secret else "меньше ↓"
        shown_text = hint if show_hint else "ИИ решил промолчать"

        self.history.insert(
            tk.END,
            f"{self.attempts:02}. {guess} — {shown_text}",
        )
        self.history.see(tk.END)

        if self.attempts >= self.max_attempts:
            self.lose(phrase)
            return

        self.result.config(
            text=(
                f"Подсказка: {shown_text}\n"
                f"Попыток: {self.attempts} из "
                f"{self.max_attempts}\n"
                f"ИИ: {phrase}"
            ),
            fg="#ffd166",
        )

    def win(self):
        self.stop_animation()
        self.button.config(state="disabled")
        self.entry.config(state="disabled")
        self.info.config(text="Система взломана!")

        if self.level == "Лёгкий":
            self.result.config(
                text="ПОЗДРАВЛЯЮ, КОЖАНЫЙ МЕШОК!",
                font=("Segoe UI", 17, "bold"),
                fg="#62e6ff",
            )
            self.start_matrix_animation()

        elif self.level == "Средний":
            self.result.config(
                text="ПОЗДРАВЛЯЮ! ТЫ ПОБЕДИЛ!",
                font=("Segoe UI", 17, "bold"),
                fg="#ffd166",
            )
            self.start_fireworks()

        else:
            self.result.config(
                # ИЗМЕНИТЬ ЗДЕСЬ: текст победы на уровне «Ветеран»
                text="ПОЗДРАВЛЯЮ, ВЕТЕРАН! ТЫ ПОБЕДИЛ!",
                font=("Segoe UI", 15, "bold"),
                fg="#ff9fba",
            )
            self.start_explosions()

    def lose(self, phrase):
        self.stop_animation()
        self.show_poop_background()

        self.button.config(state="disabled")
        self.entry.config(state="disabled")
        self.info.config(text=f"Загаданное число: {self.secret}")

        self.result.config(
            text=(
                "Ничего страшного — ИИ вас простит\n"
                f"ИИ: {phrase}"
            ),
            font=("Segoe UI", 11, "bold"),
            fg="#ff6b9d",
        )

    def stop_animation(self):
        if self.animation_job is not None:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

        self.canvas.delete("matrix")
        self.canvas.delete("fireworks")
        self.canvas.delete("explosions")

    def show_poop_background(self):
        self.canvas.delete("poop")

        for _ in range(45):
            self.canvas.create_text(
                random.randint(10, 810),
                random.randint(10, 510),
                text="💩",
                font=("Segoe UI Emoji", random.randint(18, 38)),
                tags="poop",
            )

    def new_game(self):
        self.stop_animation()
        self.canvas.delete("poop")

        self.secret = random.randint(1, 100)
        self.attempts = 0
        self.reset_phrases()
        self.history.delete(0, tk.END)

        self.entry.config(state="normal")
        self.button.config(
            state="normal",
            bg="#695cff",
            fg="white",
        )
        self.entry.delete(0, tk.END)
        self.button.place(x=190, y=220)

        self.update_labels()
        self.entry.focus()

    def start_matrix_animation(self):
        self.matrix_animation()

    def matrix_animation(self):
        self.canvas.delete("matrix")

        for _ in range(55):
            self.canvas.create_text(
                random.randint(0, 820),
                random.randint(0, 520),
                text=random.choice("0123456789"),
                fill=random.choice(
                    ["#62e6ff", "#695cff", "#a78bfa", "#e8ecff"]
                ),
                font=(
                    "Cascadia Code",
                    random.randint(11, 24),
                    "bold",
                ),
                tags="matrix",
            )

        self.animation_job = self.root.after(
            120,
            self.matrix_animation,
        )

    def start_fireworks(self):
        self.fireworks_animation()

    def fireworks_animation(self):
        self.canvas.delete("fireworks")

        colors = [
            "#ffadad",
            "#ffd6a5",
            "#fdffb6",
            "#caffbf",
            "#9bf6ff",
            "#bdb2ff",
            "#ffc6ff",
        ]

        for _ in range(10):
            center_x = random.randint(50, 770)
            center_y = random.randint(50, 470)
            color = random.choice(colors)

            for _ in range(18):
                x = center_x + random.randint(-65, 65)
                y = center_y + random.randint(-65, 65)

                self.canvas.create_oval(
                    x,
                    y,
                    x + 6,
                    y + 6,
                    fill=color,
                    outline="",
                    tags="fireworks",
                )

        self.animation_job = self.root.after(
            300,
            self.fireworks_animation,
        )

    def start_explosions(self):
        self.explosion_animation()

    def explosion_animation(self):
        self.canvas.delete("explosions")

        colors = [
            "#ff6b6b",
            "#ffd166",
            "#ff9f1c",
            "#ffffff",
            "#ff6b9d",
        ]

        for _ in range(130):
            x = random.randint(0, 820)
            y = random.randint(0, 520)
            size = random.randint(4, 13)

            self.canvas.create_oval(
                x,
                y,
                x + size,
                y + size,
                fill=random.choice(colors),
                outline="",
                tags="explosions",
            )

        self.animation_job = self.root.after(
            100,
            self.explosion_animation,
        )


if __name__ == "__main__":
    root = tk.Tk()

    icon_path = resource_path("guess_icon.ico")
    if icon_path.exists():
        root.iconbitmap(default=str(icon_path))

    GuessGame(root)
    root.mainloop()



