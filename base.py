#!/usr/bin/env python3

from base64 import b64decode
from functools import reduce
import shutil
import os

from PIL import Image

imdata = """COLOR_DATA"""

im = Image.frombytes("RGB", (400, 400), b64decode(imdata))

os.environ["TERM"] = "xterm-256color"


# Ported from bash version in
# https://unix.stackexchange.com/a/269085/68824
def palette_256():
    # Base colors
    for i in range(16):
        base = i
        mul = 128
        if i == 7:
            mul = 192
        elif i == 8:
            base = 7
        elif i > 8:
            mul = 255

        r = mul if base & 1 else 0
        g = mul if base & 2 else 0
        b = mul if base & 4 else 0
        yield i, (r, g, b)

    # RGB section
    for i in range(16, 232):
        rgb_index = [
            (i - 16) // 36,
            ((i - 16) // 6) % 6,
            (i - 16) % 6,
        ]
        rgb = [0 if val == 0 else val * 40 + 55 for val in rgb_index]
        yield i, rgb

    # 16-value grayscale
    for i in range(232, 256):
        gray = (i - 232) * 10 + 8
        rgb = (gray, gray, gray)
        yield i, rgb


def get_closest_color_256index(target_rgb):
    # return 16 + reduce(
    #     lambda acc, val: acc * 6 + 0 if val < 75 else (val - 35) // 40, target_rgb, 0
    # )

    index, rgb = min(
        palette_256(),
        key=lambda irgb: sum((t - p) ** 2 for t, p in zip(target_rgb, irgb[1])),
    )
    return index


class AlternateScreen:
    def __enter__(self):
        print("\0337\033[?47h", end="")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("\033[2J\033[?47l\0338", end="")


class HideCursor:
    def __enter__(self):
        print("\033[?25h", end="")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("\033[?25l", end="")


def ansi_print_sequence(image, size=None, skip_last_pixel=True):
    if size is None:
        size = shutil.get_terminal_size()

    image = image.resize(size)

    width, height = size
    for i in range(height):
        for j in range(width):
            if not skip_last_pixel or i + 1 < height or j + 1 < width:
                rgb = image.getpixel((j, i))
                color_index = get_closest_color_256index(rgb)
                yield f"\033[48;5;{color_index}m"
                yield " "

    yield "\033[0m"


def main():
    to_print = "".join(ansi_print_sequence(im))

    with AlternateScreen(), HideCursor():
        print(to_print, end="")
        input()


if __name__ == "__main__":
    main()
