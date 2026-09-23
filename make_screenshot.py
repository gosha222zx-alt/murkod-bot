"""Делает скриншот экрана через 5 секунд."""
import time
from pathlib import Path

from PIL import ImageGrab

print("Скриншот будет сделан через 5 секунд.")
print("Сейчас переключись на окно, которое надо снять (виджет или Telegram).")
for i in range(5, 0, -1):
    print(f"  {i}...")
    time.sleep(1)

print("Снимаю!")
img = ImageGrab.grab()

out = Path(__file__).parent / "screenshots" / "screenshot.png"
out.parent.mkdir(exist_ok=True)
img.save(out)
print(f"Готово: {out}")