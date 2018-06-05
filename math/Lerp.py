'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2014-02-189 15:52:50>
Released under the MIT License
'''


import threading
import time
import equation


# t : time
# b : starting value
# c : change(start-end)
# d : duration


# the default thread frequency (w/o computing time)
Hz60 = 0.016666


class Clock(threading.Thread):
    ''' this is a milli-precision clock
        no need to ask for time.time all the time :)
    '''
    Time = 0
    running = True

    def __init__(_):
        threading.Thread.__init__(_)
        # _._stopevent = threading.Event( ) # not on windows. It's heavy
        # use time.sleep instead
        _.start()

    def run(_):
        while Clock.running:
            Clock.Time = time.time()
            time.sleep(0.001)

    @staticmethod
    def stop(): Clock.running = False

    def __del__(_):
        Clock.stop() # todo : check


# don't forget to stop it when exiting the main loop
clock = Clock()



class Lerp(threading.Thread):

    # gonna need a merge struct over kwargs on that one
    def __init__(_,
                 x,
                 equation=equation.linear,
                 start=0,
                 end=1.0,
                 duration=1.0,
                 delay=0,
                 hold=0,
                 onComplete=lambda:None):

        threading.Thread.__init__(_)
        _.pf = x
        #starting value
        _.begin = float(start)
        #ending value
        _.end = float(end)
        #last for..
        _.duration = float(duration)
        # interpolation function
        _.equation = equation
        #print(_.equation.__name__)
        _.delay = delay
        # how much to hold between iterations
        _.hold = hold
        # a call func
        _.onComplete = onComplete # the ending functor
        #if not _.onComplete:
        #    print ("OK:", _.onComplete.__name__)
        #the time frame of reference
        _.time = 0
        _.normalizedTime = 0 # normalized 0-1 time frame
        _.elapsed = 0
        _.running = True

    def value(_):
        return _.pf[0]


    def run(_):
        _._stopevent.wait(_.delay)
        _.on = True
        startTime = time.time()
        b = _.begin
        d = _.duration
        t = 0
        c = _.end-_.begin
        while _.running: # not _._stopevent.isSet() :
            # carefull here :
            # shall the computing frequency be too high
            # and t will get out of tracks
            _.normalizedTime = _.time/_.duration
            if t > d:
                _.onComplete()
                _.stop()
            else:
                #assign to the _pointer_
                _.pf[0] = _.equation(t,b,c,d)
                time.sleep(_.hold)

            #print("%.3f << %.3f/ %.3f / %.3f / %.3f" % (_.pf[0], t,b,c,d) )
            #print("%.3f / %.3f %x" % (t,d, t<d) )

            # wait a few micro to lower the computing Hz
            #_._stopevent.wait(1.0/1000000)
            t = _.time = Clock.time - startTime
        #print "thread terminated"

    def stop(_):
        _.running = False
        _._stopevent.set( )



class Lerpf(threading.Thread):

    def __init__(_,
                 x=[0],
                 func=lambda x :None,
                 equation=equation.linear,
                 start=0,
                 end=1.0,
                 duration=1.0,
                 delay=0,
                 hold=0,
                 onComplete=lambda:None):

        threading.Thread.__init__(_)
        _.x = x
        # a call func
        _.func = func
        #starting value
        _.begin = float(start)
        #ending value
        _.end = float(end)
        #last for..
        _.duration = float(duration)
        # interpolation function
        _.equation = equation
        _.delay = delay
        # how much to hold between iterations
        _.hold = hold

        _.onComplete = onComplete # the ending functor
        #if not _.onComplete:
        #    print ("OK:", _.onComplete.__name__)
        #the time frame of reference
        _.time = 0
        _.normalizedTime = 0 # normalized 0-1 time frame
        _.elapsed = 0
        #_._stopevent = threading.Event( )
        _.running = True


        ''''

        todo : set the path depening on the initialization
        (no test inside)
        '''

    def value(_):
        return _.x[0]


    def run(_):
        t = 0
        b = _.begin
        d = _.duration
        c = _.end-_.begin
        time.sleep(_.delay)
        startTime = time.time()
        _.running = True
        while _.running: # not _._stopevent.isSet() :
            # carefull here :
            # shall the computing frequency be too high
            # and t will get out of tracks
            _.normalizedTime = t/_.duration
            if t > d:
                _.func(_.end)
                #'''
                if _.onComplete:
                    _.onComplete()
                '''
                try:
                    _.onComplete()
                except Error:
                    import traceback # a missing stackframe here
                    traceback.print_exc()
                #'''
                _.stop()
            else:
                _.x[0] = _.equation(t,b,c,d)
                _.func(_.x[0])
                time.sleep(_.hold + 0.001)

            #print("%.3f << %.3f/ %.3f / %.3f / %.3f" % (_.pf[0], t,b,c,d) )
            # wait a few micro to lower the computing Hz
            #_._stopevent.wait(1.0/1000000)

            #t = _.time = time.time() - startTime
            t = _.time = Clock.Time - startTime

    def stop(_):
        _.running = False
        #print(_,'finish')

        #_.join()
        #del(_)



# try to not confuse with the CLASS
def lerp(
    x=[0],
    func=lambda x :None,
    equation=equation.linear,
    start=0,
    end=1.0,
    duration=1.0,
    delay=0, # debug purpose
    hold=Hz60,
    onComplete=None
):Lerpf(x,func,equation,start,end,duration,delay,hold,onComplete).start()




class Schedule(threading.Thread):

    def __init__(_,t, func, params):
        threading.Thread.__init__(_)
        _.t = t
        _.func = func
        _.params = params
        _.start()

    def run(_):
        time.sleep(_.t)
        _.func(*_.params)


