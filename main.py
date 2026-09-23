import asyncio
import json
import logging
import os
from datetime import date
from pathlib import Path

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ChatAction
from aiogram.filters import Command, CommandStart
from aiogram.types import FSInputFile, Message
from dotenv import load_dotenv
from groq import Groq

from app.guess_bot import (
    build_game_response,
    build_stats_response,
    build_top_response,
    parse_guess,
)
from app.guess_game import GuessGame
from app.game_storage import GameStorage
from app.career import build_career_response, build_market_response
from app.project_tracker import ProjectStorage
from weekly_report import build_report
from daily_learning import (
    build_done_response,
    build_progress_response,
    build_today_response,
    get_day_number,
    get_today_lesson,
    load_plan,
)


load_dotenv()

MODEL_NAME = "openai/gpt-oss-20b"
TRANSCRIPTION_MODEL = "whisper-large-v3-turbo"
MAX_HISTORY_MESSAGES = 15
AVATAR_VIDEO = Path(__file__).with_name("telegram_avatar.mp4")
DATA_DIR = Path(os.getenv("MURKOD_DATA_DIR", Path(__file__).parent))
DATA_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_FILE = DATA_DIR / "conversation_history.json"
GAMES_DATABASE = DATA_DIR / "games.sqlite3"

SYSTEM_PROMPT = (
    "Тебя зовут Муркод. Ты кот-ассистент и наставник по программированию: "
    "доброжелательный, наблюдательный, с лёгким кошачьим юмором, но без лишней "
    "воды. Помогай пользователю развивать Python-проекты, разбирать ошибки, "
    "планировать обучение и превращать навыки в доход. Оценивай прогресс честно: "
    "отделяй уже доказанные навыки от предположений. Предлагай актуальные ниши "
    "рынка, но не выдавай неподтверждённые сведения за свежую статистику; советуй "
    "проверять спрос по вакансиям и заказам. Для каждого направления объясняй, "
    "что пользователь может начать делать уже сейчас, какой следующий навык нужен "
    "и какой проект положить в портфолио. Отвечай на языке пользователя."
)

router = Router()
conversation_history: dict[str, list[dict[str, str]]] = {}
active_games: dict[int, GuessGame] = {}
game_storage = GameStorage(GAMES_DATABASE)
project_storage = ProjectStorage(DATA_DIR / "projects.sqlite3")


def remember_player(message: Message) -> None:
    user = message.from_user
    display_name = user.full_name if user is not None else f"Игрок {message.chat.id}"
    game_storage.save_player(message.chat.id, display_name)


def load_history() -> None:
    global conversation_history
    if not HISTORY_FILE.exists():
        return
    try:
        data = json.loads(HISTORY_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            conversation_history = data
    except (OSError, json.JSONDecodeError):
        logging.exception("Не удалось загрузить историю")


def save_history() -> None:
    try:
        HISTORY_FILE.write_text(
            json.dumps(conversation_history, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        logging.exception("Не удалось сохранить историю")


def load_active_games() -> None:
    active_games.update(game_storage.load_all())


def get_groq_client() -> Groq:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY не задан в файле .env")
    return Groq(api_key=api_key)


def ask_groq(chat_id: int, text: str) -> str:
    history = conversation_history.setdefault(str(chat_id), [])
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": text},
    ]
    response = get_groq_client().chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
    )
    return response.choices[0].message.content or "Ассистент пока не смог сформировать ответ."


def transcribe_voice(voice_path: Path) -> str:
    with voice_path.open("rb") as audio_file:
        transcription = get_groq_client().audio.transcriptions.create(
            file=(voice_path.name, audio_file.read()),
            model=TRANSCRIPTION_MODEL,
        )
    return transcription.text


def add_to_history(chat_id: int, user_text: str, assistant_text: str) -> None:
    history = conversation_history.setdefault(str(chat_id), [])
    history.extend([
        {"role": "user", "content": user_text},
        {"role": "assistant", "content": assistant_text},
    ])
    conversation_history[str(chat_id)] = history[-MAX_HISTORY_MESSAGES:]
    save_history()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    if AVATAR_VIDEO.exists():
        await message.answer_video(
            video=FSInputFile(AVATAR_VIDEO),
            caption="Муркод на связи. Твой кот-ассистент готов помогать.",
        )
    await message.answer(
        "Пиши вопрос или отправь голосовое сообщение.\n"
        "Команда /help покажет полный список возможностей."
    )


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "Возможности Муркода:\n\n"
        "Общение:\n"
        "- отправь текстовый или голосовой вопрос\n"
        "- /clear — очистить историю диалога\n\n"
        "Игра «Угадай число»:\n"
        "- /guess — начать игру\n"
        "- /reset — сбросить текущую игру\n"
        "- /stats — твоя статистика\n"
        "- /top — рейтинг игроков\n\n"
        "Обучение Python:\n"
        "- /today — сегодняшний учебный шаг\n"
        "- /done — отметить шаг выполненным\n"
        "- /progress — прогресс обучения\n"
        "- /career — оценка навыков и направления для заработка\n"
        "- /market — идеи ниш и проектов для портфолио\n"
        "- /report — недельный отчёт по задачам виджета\n"
        "- /myid — узнать свой chat_id (для виджета)"
    )


@router.message(Command("myid"))
async def myid_handler(message: Message) -> None:
    await message.answer(
        f"Твой chat_id: <code>{message.chat.id}</code>",
        parse_mode="HTML",
    )


@router.message(Command("career"))
async def career_handler(message: Message) -> None:
    remember_player(message)
    stats = game_storage.get_stats(message.chat.id)
    completed_days = game_storage.get_completed_learning_days(message.chat.id)
    plan = load_plan()
    snapshot = {
        "completed_days": len(completed_days),
        "total_days": len(plan["days"]),
        "games": stats["games"],
        "wins": stats["wins"],
        "losses": stats["losses"],
    }
    await message.answer(build_career_response(snapshot))


@router.message(Command("market"))
async def market_handler(message: Message) -> None:
    await message.answer(build_market_response())


@router.message(Command("report"))
async def report_handler(message: Message) -> None:
    await message.answer(build_report(project_storage))


@router.message(Command("guess"))
async def guess_start_handler(message: Message) -> None:
    remember_player(message)
    game = GuessGame()
    active_games[message.chat.id] = game
    game_storage.save(message.chat.id, game)
    await message.answer(
        "Игра началась! Я загадал число от 1 до 100.\n"
        "У тебя 4 попытки. Отправь число."
    )


@router.message(Command("reset"))
async def guess_reset_handler(message: Message) -> None:
    remember_player(message)
    game = active_games.get(message.chat.id)
    if game is None:
        game = GuessGame()
        active_games[message.chat.id] = game
        game_storage.save(message.chat.id, game)
        await message.answer("Активной игры не было, поэтому я начал новую. Отправь число от 1 до 100.")
        return

    game.reset()
    game_storage.save(message.chat.id, game)
    await message.answer("Игра сброшена. Я снова загадал то же число. Отправь число от 1 до 100.")


@router.message(Command("clear"))
async def clear_handler(message: Message) -> None:
    conversation_history.pop(str(message.chat.id), None)
    save_history()
    await message.answer("История очищена. Иногда полезно освободить место на подоконнике.")


@router.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    remember_player(message)
    stats = game_storage.get_stats(message.chat.id)
    await message.answer(build_stats_response(stats))


@router.message(Command("top"))
async def top_handler(message: Message) -> None:
    remember_player(message)
    players = game_storage.get_top()
    await message.answer(build_top_response(players))


@router.message(Command("today"))
async def today_handler(message: Message) -> None:
    await message.answer(build_today_response(load_plan(), date.today()))


@router.message(Command("done"))
async def done_handler(message: Message) -> None:
    remember_player(message)
    plan = load_plan()
    today = date.today()
    lesson = get_today_lesson(plan, today)
    if lesson is None:
        await message.answer("Сегодня нет урока для отметки.")
        return

    day_number = get_day_number(plan, today)
    is_new_completion = game_storage.mark_learning_day(message.chat.id, day_number)
    await message.answer(
        build_done_response(day_number, lesson, already_done=not is_new_completion)
    )


@router.message(Command("progress"))
async def progress_handler(message: Message) -> None:
    remember_player(message)
    plan = load_plan()
    completed_days = game_storage.get_completed_learning_days(message.chat.id)
    await message.answer(build_progress_response(plan, completed_days))


async def process_guess_message(message: Message) -> None:
    remember_player(message)
    game = active_games[message.chat.id]
    if game.finished:
        await message.answer("Эта игра уже закончена. Запусти /guess для нового раунда.")
        return

    value = parse_guess(message.text)
    if value is None:
        await message.answer("Отправь целое число от 1 до 100.")
        return

    try:
        result = game.guess(value)
    except ValueError as error:
        await message.answer(str(error))
        return

    game_storage.save(message.chat.id, game)
    if result in {"win", "lose"}:
        game_storage.record_result(message.chat.id, result, game.attempts)
    await message.answer(build_game_response(result, game))


@router.message(lambda message: message.voice is not None)
async def voice_handler(message: Message, bot: Bot) -> None:
    chat_id = message.chat.id
    voice_path = Path(f"voice_{chat_id}.ogg")
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        telegram_file = await bot.get_file(message.voice.file_id)
        await bot.download_file(telegram_file.file_path, voice_path)
        text = await asyncio.to_thread(transcribe_voice, voice_path)
        answer = await asyncio.to_thread(ask_groq, chat_id, text)
        add_to_history(chat_id, text, answer)
        await message.answer(f"🎤 Ты сказал: «{text}»\n\n{answer}")
    except Exception:
        logging.exception("Ошибка обработки голосового сообщения")
        await message.answer("Не удалось услышать голос. Попробуй ещё раз, мяу.")
    finally:
        voice_path.unlink(missing_ok=True)


@router.message()
async def text_handler(message: Message, bot: Bot) -> None:
    if not message.text:
        return

    chat_id = message.chat.id
    if chat_id in active_games and not message.text.startswith("/"):
        await process_guess_message(message)
        return

    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    try:
        answer = await asyncio.to_thread(ask_groq, chat_id, message.text)
        add_to_history(chat_id, message.text, answer)
        await message.answer(answer)
    except Exception:
        logging.exception("Ошибка обращения к Groq API")
        await message.answer("Groq сейчас недоступен. Попробуй ещё раз немного позже.")


async def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в файле .env")

    load_history()
    load_active_games()
    bot = Bot(token=token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router)
    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
