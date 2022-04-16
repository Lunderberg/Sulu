#!/usr/bin/env python3

import argparse
import base64
import os
import textwrap

from PIL import Image


def main(args):
    sulu = open("base.py").read()

    im = Image.open("sulu.jpg")
    im = im.resize((400, 400))
    image_string = base64.b64encode(im.tobytes()).decode("ascii")
    image_string = "\n".join(textwrap.wrap(image_string))
    sulu = sulu.replace("COLOR_DATA", image_string)

    chart = open("color_chart.txt").read()
    sulu = sulu.replace("COLOR_CHART", chart)

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
