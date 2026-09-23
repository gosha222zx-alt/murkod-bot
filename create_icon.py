from PIL import Image, ImageDraw, ImageFont

image = Image.new("RGBA", (256, 256), "#080b18")
draw = ImageDraw.Draw(image)

draw.rounded_rectangle(
    (8, 8, 248, 248),
    radius=35,
    fill="#252344",
    outline="#62e6ff",
    width=6,
)

# Робот
draw.rounded_rectangle(
    (60, 75, 196, 190),
    radius=25,
    fill="#b8c2df",
)
draw.rectangle((78, 48, 178, 82), fill="#62e6ff")
draw.line((128, 48, 128, 25), fill="#e8ecff", width=6)
draw.ellipse((119, 15, 137, 33), fill="#ffd166")

# Лицо
draw.ellipse((88, 105, 110, 127), fill="#080b18")
draw.ellipse((146, 105, 168, 127), fill="#080b18")
draw.arc((96, 118, 160, 168), 10, 170, fill="#080b18", width=7)

# Число 100
font = ImageFont.truetype(
    r"C:\Windows\Fonts\segoeuib.ttf",
    42,
)
draw.rounded_rectangle(
    (35, 198, 221, 245),
    radius=12,
    fill="#080b18",
)
draw.text((48, 198), "100", font=font, fill="#fdffb6")
image = image.convert("RGBA")

image.save(
    r"D:\python_basic_project\guess_icon.ico",
    format="ICO",
    sizes=[
        (256, 256),
        (128, 128),
        (64, 64),
        (48, 48),
        (32, 32),
        (16, 16),
    ],
)


print("Корректная иконка создана.")