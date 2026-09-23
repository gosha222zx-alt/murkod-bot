def greet_user(name: str) -> str:
    """Возвращает приветствие пользователю."""
    return f"Привет, {name}! Это базовый проект на Python."


def build_report(items: list[str]) -> dict:
    """Формирует простой словарь с данными."""
    return {
        "count": len(items),
        "items": items,
    }
