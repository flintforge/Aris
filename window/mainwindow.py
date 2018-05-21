'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''

import os
import system
import pyglet, sys
from pyglet.window import Window
from pyglet import image

'''
really needs the lose focus event
'''

ICON_PATH = 'GFX'

def run(ScreenCls,width=1024, height=768, core=False):

    '''
    config = pyglet.gl.Config(
        double_buffer=True,
        sample_buffers=1, samples=16,
        stencil_size=8,
    )
    '''
    icons = [   image.load(os.path.join(ICON_PATH,'icon%i.png' % x))
                for x in (16,32,64,128) ]

    window = Window(caption=system.__name__, resizable=True,
                    vsync=True, width=width, height=height)
    window.set_icon(*icons)

    try:
        screen = ScreenCls(window)
    except Exception as e:
        print(e)
        sys.exit(-2)

    @window.event
    def on_draw():
        screen.draw()

    @window.event
    def on_key_press(symbol, modifiers):
        screen.on_key_press(symbol,modifiers)

    @window.event
    def on_key_release(symbol, modifiers):
        screen.on_key_release(symbol,modifiers)

    @window.event
    def on_mouse_motion(x, y, dx, dy):
        screen.on_mouse_motion(x, y, dx, dy)

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        screen.on_mouse_press(x, y, button, modifiers)

    @window.event
    def on_mouse_drag(x, y, dx, dy, button, modifiers):
        screen.on_mouse_drag(x, y, dx, dy, button, modifiers)

    @window.event
    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        screen.on_mouse_scroll(x, y, scroll_x, scroll_y)

    @window.event
    def on_resize(width, height):
        screen.resize(width, height)


    pyglet.clock.schedule_interval(screen.update, 1/60.)
    pyglet.clock.schedule_interval(screen.clock, 1.)

    pyglet.app.run()

