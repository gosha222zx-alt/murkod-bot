e) -> None:
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        current = personality.get(message.chat.id, DEFAULT_PERSONA)
        await message.answer(
            f"Текущая личность: <b>{current}</b>\n"
            f"Доступные: {', '.join(PERSONAS.keys())}\n"
            f"Пример: <code>/persona pirate</code>",
            parse_mode="HTML",
        )
        return
    name = args[1].strip().lower()
    if name not in PERSONAS:
        await message.answer(
            f"Нет такой личности. Доступные: {', '.join(PERSONAS.keys())}"
        )
        return
    personality[message.chat.id] = name
    conversation_history.pop(message.chat.id, None)
    save_history(conversation_history)
    await message.answer(f"Готово! Теперь я — {name}. История сброшена.")

# --- Обработка голосовых ---
@router.message(lambda m: m.voice is not None)
async def voice_handler(message: Message, bot: Bot) -> None:
    chat_id = message.chat.id
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    voice_path = f"voice_{chat_id}.ogg"
    try:
        file = await bot.get_file(message.voice.file_id)
        await bot.download_file(file.file_path, voice_path)

        text = await asyncio.to_thread(transcribe_voice, voice_path)
        await message.answer(f"🎤 Ты сказал: «{text}»")

        answer = await asyncio.to_thread(ask_groq, chat_id, text)
        await message.answer(answer)

        conversation_history[chat_id].append({"role": "user", "content": text})
        conversation_history[chat_id].append({"role": "assistant", "content": answer})
        if len(conversation_history[chat_id]) > MAX_HISTORY_MESSAGES:
            conversation_history[chat_id] = conversation_history[chat_id][-MAX_HISTORY_MESSAGES:]
        save_history(conversation_history)
    except Exception:
        logging.exception("Ошибка при обработке голосового")
        await message.answer("Не удалось обработать голосовое, попробуй ещё раз.")
    finally:
        if os.path.exists(voice_path):
            os.remove(voice_path)

# --- Обработка текста ---
@router.message()
async def text_handler(message: Message, bot: Bot) -> None:
    if not message.text:
        return

    chat_id = message.chat.id
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

    try:
        answer = await asyncio.to_thread(ask_groq, chat_id, message.text)
    except Exception:
        logging.exception("Ошибка при обращении к Groq API")
        await message.answer("Не удалось получить ответ от Groq. Попробуй позже.")
        return

    await message.answer(answer)

    conversation_history[chat_id].append({"role": "user", "content": message.text})
    conversation_history[chat_id].append({"role": "assistant", "content": answer})
    if len(conversation_history[chat_id]) > MAX_HISTORY_MESSAGES:
        conversation_history[chat_id] = conversation_history[chat_id][-MAX_HISTORY_MESSAGES:]
    save_history(conversation_history)

async def main() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан в файле .env")

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main()) Messag