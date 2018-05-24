'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''

from lang.dictmixins import DictMixins
from files.filemembers import Resource

class MixinResource:

    def __init__(_, sources):
        DictMixins.__init__(_, sources)
        # reloadable file resources
        Resource.load(sources, _)

    def update(_, dt):
        pass

    def __del__():
        for m in _.resources:
            del(_.__dict__[m])
