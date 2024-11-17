from pathlib import Path

from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

base_dir = Path(__file__).resolve().parent
static_dir = base_dir / "static"

img = Image.new("RGB", (700, 170), (247, 195, 30, 255))
img2 = Image.new("RGB", (50, 170), (13, 113, 219, 255))
font = ImageFont.truetype(static_dir / "fonts/UKNumberPlate.ttf", 160)


def create_image(reg: str) -> Image:
    """Creates a visual registration plate"""
    combined_width = img.width + img2.width
    combined_height = max(img.height, img2.height)

    combined_img = Image.new("RGB", (combined_width, combined_height))

    combined_img.paste(img2, (0, 0))
    combined_img.paste(img, (img2.width, 0))
    
    draw = ImageDraw.Draw(combined_img)
    # + 20 pixels for a hacky fix to keep the text centered due to the offset of img2
    draw.text(xy=((combined_width / 2) + 20, combined_height / 2), text=reg.upper(), fill="#000000", font=font, anchor="mm", align="center")

    return combined_img


