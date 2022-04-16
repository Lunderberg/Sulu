#!/usr/bin/env python3

from base64 import b64decode
import os

import curses
from PIL import Image

colorchart = """COLOR_CHART"""
colorchart = colorchart.split()

imdata = """COLOR_DATA"""

im = Image.frombytes("RGB", (400, 400), b64decode(imdata))

os.environ["TERM"] = "xterm-256color"

colors = []


def init_colors():
    global colors
    colors = []
    offset = 0
    for num, code in zip(colorchart[::2], colorchart[1::2]):
        num = int(num)
        r = int(code[1:3], base=16)
        g = int(code[3:5], base=16)
        b = int(code[5:7], base=16)
        try:
            curses.init_pair(num + offset, num, num)
        except curses.error:
            pass
        colors.append((num + offset, r, g, b))


def closest_color(r, g, b):
    target = (r, g, b)
    index = min(
        colors,
        key=lambda irgb: sum(
            (val - target_val) ** 2 for val, target_val in zip(target, irgb[1:])
        ),
    )[0]
    return curses.color_pair(index)


colors_used = {}


def curses_main(stdscr):
    global im, colors_used

    height, width = stdscr.getmaxyx()
    im = im.resize((width, height))
    init_colors()

    for i in range(height):
        for j in range(width):
            r, g, b = im.getpixel((j, i))
            if i == height - 1 and j == width - 1:
                continue
            stdscr.addch(i, j, " ", closest_color(r, g, b))
    stdscr.refresh()
    stdscr.getch()


curses.wrapper(curses_main)
