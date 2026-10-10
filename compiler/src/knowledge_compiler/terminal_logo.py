from __future__ import annotations

from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image


LOGO_PATH = Path(__file__).parent / "assets" / "knowledge-compiler-mark.svg"

AMBER = (253, 168, 42)       
GRAPHITE = (66, 66, 66)      
BACKGROUND = (23, 23, 23)    

RESET = "\033[0m"


def _nearest_brand_color(
    pixel: tuple[int, int, int],
) -> tuple[int, int, int]:
    palette = (AMBER, GRAPHITE, BACKGROUND)

    return min(
        palette,
        key=lambda color: sum(
            (pixel[channel] - color[channel]) ** 2
            for channel in range(3)
        ),
    )


def render_terminal_logo(
    width: int = 32,
) -> list[str]:
    if width < 8:
        raise ValueError("Logo width must be at least 8 characters.")

    if not LOGO_PATH.is_file():
        raise FileNotFoundError(
            f"Knowledge Compiler logo not found: {LOGO_PATH}"
        )

    png_data = cairosvg.svg2png(
        url=str(LOGO_PATH),
        output_width=width,
        output_height=width,
    )

    with Image.open(BytesIO(png_data)) as source:
        rgba = source.convert("RGBA")

    background = Image.new("RGBA", rgba.size, (*BACKGROUND, 255))
    image = Image.alpha_composite(background, rgba).convert("RGB")

    pixels = image.load()
    lines: list[str] = []

    for y in range(0, width, 2):
        parts: list[str] = []
        previous_colors = None

        for x in range(width):
            top = _nearest_brand_color(pixels[x, y])
            bottom = _nearest_brand_color(pixels[x, y + 1])

            colors = (top, bottom)

            if colors != previous_colors:
                parts.append(
                    f"\033[38;2;{top[0]};{top[1]};{top[2]}m"
                    f"\033[48;2;{bottom[0]};{bottom[1]};{bottom[2]}m"
                )
                previous_colors = colors

            parts.append("▀")

        parts.append(RESET)
        lines.append("".join(parts))

    return lines