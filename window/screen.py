'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''
from pyglet import canvas


class Screen:
    """ application screens for main menu, settings menu, rendering screen and so on
        think ahead :
        the events should be intercepted with or w/o further propagation
        by intermediate sub programs loaded at runtime.

        This can be used as a template, or subcast for various little pre/post effects,
        default show/hides, etc
    """

    def __init__(_,window):
        _.width, _.height = (window.width, window.height) if window else (256,256)
        _.window = window
        scr = canvas.get_display().get_default_screen()
        #print (_.get_modes())
        #scr = get_platform().get_default_display().get_default_screen()
        _.resolution = scr.width, scr.height
        window.set_location(int(scr.width/2 - _.width/2),int(scr.height/2 - _.height/2))


    def get_modes(_):
        scr = canvas.get_display().get_default_screen()
        modes = set()
        for mode in scr.get_modes():
            modes.update({(mode.width,mode.height)})
        print (modes)

        '''
        existing ratio :
        3:2, 5:2 , 18:10, 16:9, 16:10
        '''
        for sz in modes:
            print(sz, sz[0]/sz[1], sz[0] * sz[1])
    def show(_):
        pass

    def draw(_):
        pass

    def resize(_,width, height):
        pass

    def pause(_):
        pass

    def resume(_):
        pass

    def hide(_):
        """ Called when this screen is no longer the current screen for a {@link Game}."""
        pass

    def dispose(_):
        pass

    def update(_,dt):
        pass

    def clock(_,dt):
        print('default Screen clock')
        pass

    def on_mouse_scroll(_,x, y, scroll_x, scroll_y):
        pass
