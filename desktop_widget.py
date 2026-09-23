"""Windows desktop widget for projects, tasks, and skill progress."""

from __future__ import annotations

import os
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox, ttk

from app.integrations import (
    JobItem,
    assess_with_ai,
    github_repositories,
    load_job_items,
    open_in_vscode,
    send_telegram_message,
)
from app.project_tracker import ProjectStorage
from weekly_report import build_report


DATA_DIR = Path(os.getenv("MURKOD_DATA_DIR", Path(__file__).parent))
STORAGE = ProjectStorage(DATA_DIR / "projects.sqlite3")
BG = "#10151c"
PANEL = "#18222d"
TEXT = "#edf2f7"
MUTED = "#8fa2b5"
ACCENT = "#72d6b2"
ORANGE = "#f5ae62"


class DesktopWidget:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.compact = False
        root.title("Муркод · прогресс")
        root.geometry("390x600")
        root.minsize(330, 250)
        root.configure(bg=BG)
        root.attributes("-topmost", True)
        root.protocol("WM_DELETE_WINDOW", self.hide)
        self._configure_style()
        self._build_ui()
        self.refresh()

    def _configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Widget.TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("Widget.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 18))
        style.configure("Panel.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("PanelMuted.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 9))
        style.configure("Accent.TButton", background=ACCENT, foreground="#102019", padding=(12, 7), font=("Segoe UI Semibold", 9))
        style.map("Accent.TButton", background=[("active", "#a0ead0")])
        style.configure("Ghost.TButton", background=PANEL, foreground=TEXT, padding=(8, 5), borderwidth=0)

    def _build_ui(self) -> None:
        self.body = ttk.Frame(self.root, style="Widget.TFrame", padding=18)
        self.body.pack(fill="both", expand=True)
        header = ttk.Frame(self.body, style="Widget.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Муркод", style="Title.TLabel").pack(side="left")
        ttk.Label(header, text="  WORKSPACE", style="Muted.TLabel").pack(side="left", pady=(5, 0))
        ttk.Button(header, text="—", style="Ghost.TButton", command=self.toggle_compact).pack(side="right")
        ttk.Button(header, text="×", style="Ghost.TButton", command=self.hide).pack(side="right")
        self.summary = ttk.Label(self.body, style="Muted.TLabel")
        self.summary.pack(anchor="w", pady=(4, 14))

        self.form = ttk.Frame(self.body, style="Panel.TFrame", padding=14)
        self.form.pack(fill="x", pady=(0, 14))
        ttk.Label(self.form, text="Новая задача или проект", style="Panel.TLabel").pack(anchor="w")
        self.title_entry = ttk.Entry(self.form, font=("Segoe UI", 10))
        self.title_entry.pack(fill="x", pady=(10, 7))
        self.title_entry.insert(0, "Например: Telegram-бот для заявок")
        self.description = tk.Text(self.form, height=3, wrap="word", bg="#22303d", fg=TEXT, insertbackground=TEXT, relief="flat", padx=8, pady=7, font=("Segoe UI", 9))
        self.description.pack(fill="x", pady=(0, 9))
        self.description.insert("1.0", "Что делаешь, какие технологии используешь и какой результат нужен")
        self.path_entry = ttk.Entry(self.form, font=("Segoe UI", 9))
        self.path_entry.pack(fill="x", pady=(0, 9))
        self.path_entry.insert(0, str(Path.cwd()))
        ttk.Button(self.form, text="Добавить и оценить", style="Accent.TButton", command=self.add_project).pack(anchor="e")

        ttk.Label(self.body, text="Последние задачи", style="Widget.TLabel").pack(anchor="w", pady=(0, 7))
        self.projects = tk.Listbox(self.body, bg=PANEL, fg=TEXT, selectbackground="#2b5d58", selectforeground=TEXT, relief="flat", highlightthickness=0, font=("Segoe UI", 10), activestyle="none")
        self.projects.pack(fill="both", expand=True)
        self.projects.bind("<Double-Button-1>", self.complete_selected)
        footer = ttk.Frame(self.body, style="Widget.TFrame")
        footer.pack(fill="x", pady=(12, 0))
        ttk.Button(footer, text="VS Code", style="Ghost.TButton", command=self.open_selected).pack(side="left")
        ttk.Button(footer, text="GitHub", style="Ghost.TButton", command=self.show_github).pack(side="left")
        ttk.Button(footer, text="Заявки", style="Ghost.TButton", command=self.show_jobs).pack(side="left")
        ttk.Button(footer, text="Отчёт", style="Ghost.TButton", command=self.send_report).pack(side="left")
        ttk.Button(footer, text="Выйти", style="Ghost.TButton", command=self.root.destroy).pack(side="right")

    def add_project(self) -> None:
        title = self.title_entry.get().strip()
        description = self.description.get("1.0", "end").strip()
        project_path = self.path_entry.get().strip()
        if title.startswith("Например:"):
            title = ""
        if not title:
            messagebox.showwarning("Нужен заголовок", "Напиши название задачи или проекта.", parent=self.root)
            return
        STORAGE.add_project(title, description, project_path)
        _, ai_text = assess_with_ai(title, description)
        self.title_entry.delete(0, "end")
        self.description.delete("1.0", "end")
        self.refresh()
        messagebox.showinfo("Оценка Муркода", ai_text, parent=self.root)

    def complete_selected(self, _event: tk.Event[tk.Listbox]) -> None:
        selection = self.projects.curselection()
        if not selection:
            return
        project = STORAGE.list_projects()[selection[0]]
        STORAGE.complete_project(int(project["id"]))
        self.refresh()

    def open_selected(self) -> None:
        selection = self.projects.curselection()
        if not selection:
            messagebox.showinfo("Выбор задачи", "Выбери задачу в списке.", parent=self.root)
            return
        project = STORAGE.start_project(int(STORAGE.list_projects()[selection[0]]["id"]))
        if project:
            open_in_vscode(str(project["project_path"]))
            self.refresh()

    def show_github(self) -> None:
        try:
            repositories = github_repositories()
        except Exception as error:
            messagebox.showwarning("GitHub", str(error), parent=self.root)
            return
        if not repositories:
            messagebox.showinfo("GitHub", "В аккаунте пока нет репозиториев.", parent=self.root)
            return
        webbrowser.open(repositories[0]["url"])
        messagebox.showinfo("GitHub", f"Открыт последний репозиторий: {repositories[0]['name']}", parent=self.root)

    @staticmethod
    def _job_matches_filter(job: JobItem) -> bool:
        keywords = [keyword.strip().lower() for keyword in os.getenv("JOB_KEYWORDS", "").split(",") if keyword.strip()]
        if not keywords:
            return False
        haystack = f"{job.title} {job.summary}".lower()
        return any(keyword in haystack for keyword in keywords)

    def show_jobs(self) -> None:
        jobs = load_job_items()
        if not jobs:
            messagebox.showinfo("Заявки", "Добавь RSS/Atom-адреса в JOB_FEEDS в .env или проверь JOB_KEYWORDS.", parent=self.root)
            return

        window = tk.Toplevel(self.root)
        window.title("Заявки")
        window.geometry("760x520")
        window.configure(bg=BG)
        window.transient(self.root)
        window.grab_set()
        window.protocol("WM_DELETE_WINDOW", window.destroy)

        header = ttk.Frame(window, padding=(12, 10, 12, 8), style="Widget.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text=f"Найдено: {len(jobs[:10])}", style="Widget.TLabel").pack(side="left")
        ttk.Button(header, text="Обновить", style="Ghost.TButton", command=lambda: self._refresh_jobs_window(window)).pack(side="right")

        canvas = tk.Canvas(window, bg=BG, highlightthickness=0)
        scrollbar = ttk.Scrollbar(window, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(12, 0), pady=(0, 12))
        scrollbar.pack(side="right", fill="y", pady=(0, 12))

        jobs_frame = ttk.Frame(canvas, style="Widget.TFrame")
        canvas.create_window((0, 0), window=jobs_frame, anchor="nw")
        jobs_frame.bind("<Configure>", lambda event: canvas.configure(scrollregion=canvas.bbox("all")))

        def populate_jobs() -> None:
            for child in jobs_frame.winfo_children():
                child.destroy()
            visible_jobs = jobs[:10]
            for job in visible_jobs:
                row = tk.Frame(jobs_frame, bg="#1d2a34", highlightthickness=1, highlightbackground="#2f3d4f", padx=8, pady=8)
                if self._job_matches_filter(job):
                    row.configure(bg="#163d33", highlightbackground="#4fe0a4", highlightcolor="#4fe0a4")
                row.pack(fill="x", pady=4)

                label = tk.Label(
                    row,
                    text=f"{job.title}\n{job.source}",
                    bg=row["bg"],
                    fg=TEXT,
                    justify="left",
                    anchor="w",
                    wraplength=560,
                    font=("Segoe UI", 9),
                )
                label.pack(side="left", fill="x", expand=True, padx=(0, 12))

                ttk.Button(
                    row,
                    text="Открыть",
                    style="Ghost.TButton",
                    command=lambda url=job.url: webbrowser.open(url),
                ).pack(side="right")

        populate_jobs()

    def _refresh_jobs_window(self, window: tk.Toplevel) -> None:
        jobs = load_job_items()
        content = window.winfo_children()
        if not content:
            return
        header = content[0]
        if len(header.winfo_children()) >= 2:
            label = header.winfo_children()[0]
            label.configure(text=f"Найдено: {len(jobs[:10])}")

        canvas = window.winfo_children()[-1]
        jobs_frame = canvas.winfo_children()[0]
        for child in jobs_frame.winfo_children():
            child.destroy()

        if not jobs:
            ttk.Label(jobs_frame, text="Нет заявок по текущим критериям.", style="Muted.TLabel").pack(pady=12)
            return

        for job in jobs[:10]:
            row = tk.Frame(jobs_frame, bg="#1d2a34", highlightthickness=1, highlightbackground="#2f3d4f", padx=8, pady=8)
            if self._job_matches_filter(job):
                row.configure(bg="#163d33", highlightbackground="#4fe0a4", highlightcolor="#4fe0a4")
            row.pack(fill="x", pady=4)

            tk.Label(
                row,
                text=f"{job.title}\n{job.source}",
                bg=row["bg"],
                fg=TEXT,
                justify="left",
                anchor="w",
                wraplength=560,
                font=("Segoe UI", 9),
            ).pack(side="left", fill="x", expand=True, padx=(0, 12))

            ttk.Button(
                row,
                text="Открыть",
                style="Ghost.TButton",
                command=lambda url=job.url: webbrowser.open(url),
            ).pack(side="right")

        jobs_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def send_report(self) -> None:
        try:
            send_telegram_message(build_report(STORAGE))
        except Exception as error:
            messagebox.showwarning("Telegram", str(error), parent=self.root)
            return
        messagebox.showinfo("Telegram", "Отчёт отправлен.", parent=self.root)

    def refresh(self) -> None:
        summary = STORAGE.get_summary()
        self.summary.configure(text=f"{summary['completed']} готово  ·  {summary['total']} задач  ·  {len(summary['skills'])} навыков")
        self.projects.delete(0, "end")
        for project in STORAGE.list_projects():
            marker = "●" if project["status"] == "Готово" else "○"
            skills = ", ".join(project["skills"][:3])
            self.projects.insert("end", f"{marker}  {project['title']}  ·  {project['category']}\n    {skills}")

    def toggle_compact(self) -> None:
        self.compact = not self.compact
        self.root.geometry("390x250" if self.compact else "390x600")
        if self.compact:
            self.form.pack_forget()
            self.projects.pack_forget()
        else:
            self.form.pack(fill="x", pady=(0, 14))
            self.projects.pack(fill="both", expand=True)

    def hide(self) -> None:
        self.root.iconify()


if __name__ == "__main__":
    window = tk.Tk()
    DesktopWidget(window)
    window.mainloop()