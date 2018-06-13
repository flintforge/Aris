'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
import logging
logger = logging.getLogger( 'log.%s' % __name__)
'''
has to be extended to look on_created for a peculiar directory :
the file events on that disk
'''
class FileWatcher(PatternMatchingEventHandler):
    # patterns = ["*.png"]
    watchers = []

    @classmethod
    def start(cls, cb, patterns=['*.py'], path='.'):
        observer = Observer()
        FileWatcher.watchers.append(observer)
        observer.schedule(FileWatcher(cb, patterns, observer), path=path)
        observer.start()

    @classmethod
    def stop(cls):
        [o.stop() for o in cls.watchers]
        logger.info('Filewatchers terminated')

    def __init__(self, callback, patterns, observer):
        PatternMatchingEventHandler.__init__(self, patterns)
        '''
        (self, patterns=None, ignore_patterns=None, ignore_directories=False, case_sensitive=False):
        '''
        self.callback = callback
        self.observer = observer


    def on_modified(self, event):
        logger.info('file modified %s' % event)
        self.callback(event)


# test
if __name__ == '__main__':
    import time
    import sys
    import yaml,logging.config

    logging.config.dictConfig(yaml.load(open('logging.yml', 'r')))
    twice = 0

    def cb(event):
        global twice
        print(event.src_path, event.event_type)
        # FileWatcher.stop()
        twice += 1
        if twice == 2:
            print('exited')
            FileWatcher.stop()
            sys.exit()

    #FileWatcher.start(cb, ['*.vs', '*.fs'], './filewatc')
    FileWatcher.start(cb, ['*.py'], '.')
    FileWatcher.start(cb, ['*'], './tmp')

    try:
        print('filewatcher process started')
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        FileWatcher.stop()
