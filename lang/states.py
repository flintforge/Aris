'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''

from enum import Enum

class State:

    statemodes = {}
    ''' submode for each keys if aint boolean
        kept at class level to toggle new states
        from previous ones
    '''

    def __init__(_, keys, init=False):

        assert type(keys) is list
        _.keys = keys
        for k in keys:
            _[k] = init
            _.currentMode = {} # current states for submode


    def __iter__(_):
        return iter(_.keys)

    def __getitem__(_,x):
        ''' shortcut. carefull if we erase classes bultins '''
        return _.__dict__[x]

    def __setitem__(_,x,y):
        ''' shortcut. carefull if we erase classes bultins '''
        _.__dict__[x] = y

    def bswitch(_,key): # boolean switch for key
        _[key] = not _[key]
        return _[key]

    def states(_,key,values) :
        State.statemodes[key] = list(values)# in case it's an enum
        _.currentMode[key] = 0
        _[key] = State.statemodes[key][0]
        return _[key]

    def nextItem(_,key) :
        N = _.currentMode[key] + 1
        _.currentMode[key] = N % len(_.statemodes[key])
        _[key] = _.statemodes[key][_.currentMode[key]]

    def previousItem(_,key) :
        N = _.currentMode[key] - 1
        _.currentMode[key] = N % len(_.statemodes[key])
        _[key] = _.statemodes[key][_.currentMode[key]]


# alias
State.toggle = State.nextItem


if __name__ == '__main__':

    s = State(['login','logout','mode'])
    s.states('mode',['A','B','C'])
    assert s.login is False
    s.bswitch('login')
    assert s.login is True

    assert s.mode == 'A'
    s.previousItem('mode')
    assert s.mode is 'C'
    s.nextItem('mode')
    assert s.mode is 'A'
    s.nextItem('mode')
    assert s.mode is 'B'
    s.toggle('mode')
    assert s.mode is 'C'

    t = State(['login','logout','mode'], True)
    t.states('mode',['A','B','C'])
    assert t.login is True
    t.bswitch('login')
    assert t.login is False

    CameraType = Enum('CameraType','FREE TARGET ORTHOGRAPHIC')

    t = State(['camera'])
    t.states('camera', CameraType)
    assert t.camera is CameraType.FREE


    def toggle(k):
        s.bswitch(k)

    keyboundto = {
        1:(toggle,'login'),
        2:(toggle,'logout'),
        3:(toggle,'pouet'),
    }
    try :
        for f,k in keyboundto.values():
            if k not in s.keys :
                raise Exception('%s not in registered states %s' % (k,s.keys))
    except Exception as e:
        print(e)


