#!/usr/bin/env python

import Image
import curses
from time import sleep
from random import shuffle
import os

colorchart = """COLOR_CHART"""
colorchart = colorchart.split()

imdata = """COLOR_DATA"""

im = Image.fromstring('RGB',(400,400),imdata.decode('base64'))

os.environ['TERM'] = 'xterm-256color'

colors = []
def init_colors():
    global colors
    colors = []
    offset = 0
    for num,code in zip(colorchart[::2],colorchart[1::2]):
        num = int(num)
        r = int(code[1:3],base=16)
        g = int(code[3:5],base=16)
        b = int(code[5:7],base=16)
        try:
            curses.init_pair(num+offset,num,num)
        except curses.error:
            pass
        colors.append((num+offset,r,g,b))

def closest_color(r,g,b):
    index = min(colors,
                key = lambda (i,rc,gc,bc):(rc-r)**2 + (gc-g)**2 + (bc-b)**2)[0]
    return curses.color_pair(index)

colors_used = {}
def curses_main(stdscr):
    global im,colors_used
    if not curses.has_colors():
        raise Exception('Need terminal colors enabled to proceed')

    height,width = stdscr.getmaxyx()
    im = im.resize((width,height))
    init_colors()

    for i in range(height):
        for j in range(width):
            r,g,b = im.getpixel((j,i))
            try:
                stdscr.addch(i,j,' ',closest_color(r,g,b))
            except curses.error:
                continue
    stdscr.refresh()
    stdscr.getch()

curses.wrapper(curses_main)
