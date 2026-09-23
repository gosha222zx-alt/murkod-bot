# Murkod Bot

Telegram-бот на Python с ИИ-помощником, проектным трекером, desktop-виджетом и системой автоматизации рабочего процесса.

[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![Groq](https://img.shields.io/badge/Groq-AI-FF7A00)](https://console.groq.com/)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white)](https://core.telegram.org/bots)
[![Windows](https://img.shields.io/badge/Platform-Windows-0078D4)](https://www.microsoft.com/windows)

## Что это

Этот проект объединяет несколько реальных решений:

- Telegram-бот с ИИ-помощником на aiogram
- голосовые сообщения и распознавание через Groq Whisper
- учебный трекер по Python и прогресс обучения
- игровая логика, статистика и рейтинг игроков
- desktop-виджет для управления задачами и проектами
- интеграции с GitHub, Telegram, RSS-лентами и задачами
- система витринных/офисных сценариев для автоматизации

Это не просто учебный пример, а полноценный проект-демонстрация навыков Python-разработчика: ботов, интеграций, автоматизации и desktop-приложений.

## Что умеет проект

### Telegram-бот
- диалог с ИИ через Groq API
- обработка текста и голосовых сообщений
- команда /help, /start, /career, /market, /today, /done, /progress, /guess, /stats, /top
- учёт прогресса и хранение истории сообщений
- хранение данных в SQLite
- игровая логика и рейтинг игроков
- отправка отчётов и уведомлений в Telegram

### Desktop widget
- учёт задач и проектов
- автоматическое формирование категории и навыков проекта
- AI-оценка задачи
- кнопка VS Code для открытия рабочей папки
- кнопка GitHub для открытия репозитория
- кнопка Заявки для RSS-фидов и фильтрации вакансий
- кнопка Отчёт для отправки прогресса в Telegram
- удаление старых задач при переполнении списка

## Стек

- Python 3.12+
- aiogram 3
- SQLite
- Groq API
- python-dotenv
- tkinter
- GitHub API
- RSS/Atom feed parsing
- Docker

## Архитектура проекта

- main.py — Telegram-бот
- desktop_widget.py — desktop-виджет на tkinter
- app/integrations.py — интеграции с Telegram, GitHub, RSS и AI
- app/project_tracker.py — учёт задач и проектов
- weekly_report.py — построение отчётов
- tests/ — проверка логики и хранения данных

## Быстрый старт на Windows

### 1. Клонировать проект

```powershell
git clone https://github.com/gosha222zx-alt/murkod-bot.git
cd D:\python_basic_project
```

### 2. Создать виртуальное окружение

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Установить зависимости

```powershell
pip install -r requirements.txt
```

### 4. Создать .env

Файл `.env` должен лежать в корне проекта:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
GROQ_API_KEY=your_groq_key
GITHUB_TOKEN=your_github_token
TELEGRAM_CHAT_ID=your_chat_id
JOB_FEEDS=https://freelance.habr.com/tasks.rss
JOB_KEYWORDS=telegram,python,бот,парсер
```

## Запуск Telegram-бота

```powershell
python main.py
```

После запуска бот готов к работе через Telegram.

## Запуск виджета

```powershell
python desktop_widget.py
```

Виджет откроет окно с формой добавления задач, списком проектов, GitHub, заявками, отчётом и удалением задач.

## Сборка Windows EXE

### Установить PyInstaller

```powershell
pip install pyinstaller
```

### Собрать приложение

```powershell
pyinstaller --onefile --windowed --name MurkodWidget --collect-all app --collect-all weekly_report desktop_widget.py
```

Оконный файл будет доступен в папке `dist`.

## Проверки и рутинная QA

### Рекомендуемый набор локальных проверок

1. Проверить запуск бота:
   ```powershell
   python main.py
   ```
2. Проверить запуск виджета:
   ```powershell
   python desktop_widget.py
   ```
3. Проверить базу задач:
   ```powershell
   python -m unittest tests/test_project_tracker.py -q
   ```
4. Проверить, что .env переменные читаются без ошибок
5. Проверить кнопки GitHub, Заявки, Отчёт при наличии токенов
6. Проверить поведение при пустом `JOB_KEYWORDS` и при наличии фильтра
7. Проверить удаление задач при большом количестве
8. Проверить корректность работы `VS Code` open path

## Ручная проверка по шагам

### Этап 1. Проверка окружения
- проект открывается в VS Code
- Python установлен
- зависимости установлены
- `.env` создан

### Этап 2. Проверка виджета
- окно открывается без ошибок
- поле title работает
- поле description работает
- кнопка Добавить и оценить сохраняет задачу
- список обновляется после добавления
- задача открывается в VS Code
- задача помечается как выполнена
- задача удаляется корректно

### Этап 3. Проверка интеграций
- GitHub кнопка открывает репозиторий при наличии `GITHUB_TOKEN`
- Заявки открывают список и фильтрацию по ключевым словам
- Отчёт отправляется в Telegram при наличии токенов

### Этап 4. Проверка деплоя
- проект запускается после `pip install -r requirements.txt`
- при необходимости создаётся EXE через PyInstaller
- все секреты остаются в `.env`
- приложение работает локально и без утечек ключей

## Почему это проект для портфолио

Этот проект показывает реальный уровень Python-разработчика в направлениях:

- Telegram-боты
- AI-интеграции
- desktop UI
- работа с API
- базы данных
- автоматизация
- продуктовый сценарий для повседневной работы

Для Kwork и GitHub это выглядит как законченный и практичный проект, а не просто тестовый сценарий.

## GitHub и публикация

Репозиторий можно публиковать на GitHub и использовать как демонстрацию инженерной работы. Перед публикацией важно:

1. проверить, что `.env` не попадает в репозиторий
2. убедиться, что все токены и секреты находятся локально
3. обновить README после финальных правок
4. сделать чистый git commit и push

## Деплой и дальнейшие шаги

После стабилизации локальной версии можно выполнить следующий цикл:

1. проверить проект локально
2. проверить сборку EXE
3. проверить зависимости во время установки с нуля
4. проверить работу кнопок и интеграций вручную
5. опубликовать актуальный README на GitHub
6. сделать финальный деплой и повторную проверку

## Краткий итог

Проект уже выглядит как полноценное Python-портфолио: бот, AI, desktop widget, task tracker, интеграции, рабочие сценарии и автоматизация. Чтобы довести его до лучшего состояния, главное — сделать финальную проверку, стабилизировать деплой и подтвердить ручную работу по каждому этапу.
