'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''

from .filemembers import *
import queue
import debuglog
logger = debuglog.init(__name__)

FileEventQueue = queue.Queue()

'''
def reverseLookDict(dico, item):
    return list(dico.keys())[list(dico.values()).index(item)]
'''

def FileEventQHandler(resources, obj):
    """
    among those,
    are events which need to be triggered into the gl active context.
    files are indexed by name (which is wrong and ask for a path cut)
    """

    try:
        event = FileEventQueue.get_nowait()
    except queue.Empty:
        pass
    else:
        file = event.src_path  # manage only watchdog.events.FileModifiedEvent for now
        # grab only the file name. Fixme, give them ids, use the atlas
        file = file[file.rindex('/') + 1:]
        for (k, v) in resources.items():

            it = v[1]
            if it == file:
                logger.debug('%s %s %s' % (event, file, obj.__dict__[k]))
                return Resource.reload(file, obj.__dict__[k])

            elif type(it) is list or type(it) is tuple:  # inspect the list
                for e in it:
                    if e == file:
                        logger.debug('%s %s %s' % (event, file, obj.__dict__[k]))
                        return Resource.reload(file, obj.__dict__[k])

        logger.debug(' %s but not in watch patch ( %s )' % (event.src_path, file))
