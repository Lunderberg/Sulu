# -*- python -*-

import Image

def make_sulu(target,source,env):
    sulu = open('base.py').read()

    im = Image.open('sulu.jpg')
    im = im.resize((400,400))
    sulu = sulu.replace('COLOR_DATA',im.tostring().encode('base64'))

    chart = open('color_chart.txt').read()
    sulu = sulu.replace('COLOR_CHART',chart)

    with open('sulu.py','w') as f:
        f.write(sulu)

Command('sulu.py',['sulu.jpg','color_chart.txt','base.py'],
        [make_sulu,Chmod('$TARGET',0755)])

