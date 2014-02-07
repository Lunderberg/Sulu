#!/usr/bin/env python

import Image

sulu = open('base.py').read()

im = Image.open('sulu.jpg')
im = im.resize((400,400))
sulu = sulu.replace('COLOR_DATA',im.tostring().encode('base64'))

chart = open('color_chart.txt').read()
sulu = sulu.replace('COLOR_CHART',chart)

with open('sulu.py','w') as f:
    f.write(sulu)
