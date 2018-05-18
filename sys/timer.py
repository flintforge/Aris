import time
from pyglet.clock import schedule_interval

class Timer(object):
    """a self scheduled timer"""

    def update(self,dt):
        self.time = self.start + (time.time() - self.init) * self.factor

    def __init__(self, start=0, factor=1., freq=1/120.):
        ''' if we suppose the refresh frequency is 60hz,
        the timer must run at least two times faster
        in case an out of sync rendering occurs,
        wich leads to glitches.
        recomputing the timer on every frame is safer
        if we need high fréquency or expect slowdowns.
        '''
        self.init = time.time()
        self.start = start
        self.factor = factor
        self.time = start
        schedule_interval(self.update, freq)


if __name__ == '__main__':
    import pyglet
    from threading import Thread

    timer = Timer(10,5)
    timer2 = Timer()

    def print_timer():
        while(timer2.time < 5):
            print(timer.time)
            time.sleep(1)

    Thread(target=print_timer).start()
    pyglet.app.run()

