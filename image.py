from pathlib import Path

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

base_dir = Path(__file__).resolve().parent
static_dir = base_dir / "static"

img = Image.new("RGB", (700, 170), (247, 195, 30, 255))
font = ImageFont.truetype(static_dir / "fonts/UKNumberPlate.ttf", 160)

def create_image(reg: str) -> Image:
    width, height = img.size

    draw = ImageDraw.Draw(img)
    draw.text(xy=(width / 2, height / 2), text=reg.upper(), fill="#000000", font=font, anchor="mm", align="center")

    return img


