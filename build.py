#!/usr/bin/env python3

import argparse
import base64
import functools
from gzip import GzipFile
import io
import os
import textwrap
from typing import List, Tuple, Sequence

from PIL import Image
import numpy as np

Color = Tuple[int, int, int]

# Ported from bash version in
# https://unix.stackexchange.com/a/269085/68824
def generate_palette_256() -> Sequence[Color]:
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


def get_closest_color(
    target: Color,
    palette: np.array,
):
    target = np.array(target, dtype="int32")
    return int(((palette - target) ** 2).sum(axis=1).argmin())


def main(args):
    sulu = open("base.py").read()

    image = Image.open("sulu.jpg")
    image = image.resize((400, 400))

    width, height = image.size

    palette = [rgb for i, rgb in generate_palette_256()]
    palette = np.array(palette, dtype="int32")

    indices = [
        get_closest_color(image.getpixel((j, i)), palette)
        for i in range(height)
        for j in range(width)
    ]

    data = [width % 256, width // 256, height % 256, height // 256, *indices]

    data_bytes = b"".join(i.to_bytes(1, byteorder="big") for i in data)

    fileobj = io.BytesIO()
    with GzipFile(fileobj=fileobj, mode="w") as f:
        f.write(data_bytes)
    gzipped_bytes = fileobj.getvalue()

    base64_indices = base64.b64encode(gzipped_bytes).decode("ascii")
    image_string = "\n".join(textwrap.wrap(base64_indices))
    image_string = f"\n{image_string}\n"

    sulu = sulu.replace("COLOR_DATA", image_string)

    with open("sulu.py", "w") as f:
        f.write(sulu)
    os.chmod("sulu.py", 0o755)


def arg_main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--pdb",
        action="store_true",
        help="Start a pdb post mortem on uncaught exception",
    )

    args = parser.parse_args()

    try:
        main(args)
    except Exception:
        if args.pdb:
            import pdb, traceback

            traceback.print_exc()
            pdb.post_mortem()
        raise


if __name__ == "__main__":
    arg_main()
