

import os
import system
import pyglet, sys
from pyglet.window import Window
from pyglet import image
ICON_PATH = 'GFX'


'''
in case we completly want to change screen
but rather changes the bindings of the ARIS

'''

class MainWindow(Window):

    def __init__(_, Screen ):

        super(MainWindow, _).__init__(caption=system.__name__,
                                         fullscreen=False,
                                         style=None, visible=True,
                                         width=1024,height=768,
                                         vsync=True, resizable=True
                                         )

        # todo : check the game isn't already running

        icons = [   image.load(os.path.join(ICON_PATH,'icon%i.png' % x))
                    for x in (16,32,64,128) ]

        # window = Window(caption=system.__name__, resizable=True,
        #                vsync=True, width=width, height=height)
        #window.set_icon(*icons)

        try:
            _.scene = Screen(_)
        except Exception as e:
            print(e)
            sys.exit(-2)

        #_.fps_display = pyglet.clock.ClockDisplay()
        pyglet.clock.schedule_interval(_.scene.update, 1/60.)
        pyglet.clock.schedule_interval(_.scene.clock, 1.)
        pyglet.app.run()

    def on_draw():
        _.scene.draw()

    def on_key_press(symbol, modifiers):
        _.scene.on_key_press(symbol,modifiers)

    def on_key_release(symbol, modifiers):
        _.scene.on_key_release(symbol,modifiers)

    def on_mouse_motion(x, y, dx, dy):
        _.scene.on_mouse_motion(x, y, dx, dy)

    def on_mouse_press(x, y, button, modifiers):
        _.scene.on_mouse_press(x, y, button, modifiers)

    def on_mouse_drag(x, y, dx, dy, button, modifiers):
        _.scene.on_mouse_drag(x, y, dx, dy, button, modifiers)

    def on_mouse_scroll(x, y, scroll_x, scroll_y):
        _.scene.on_mouse_scroll(x, y, scroll_x, scroll_y)

    def on_resize(width, height):
        _.scene.resize(width, height)



import logging
from logging import info
from datetime import datetime


if __name__ == '__main__':
    from Aris import RenderCore
    window = MainWindow(RenderCore)
    print('___ finished ___')
