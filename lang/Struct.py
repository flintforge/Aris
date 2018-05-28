'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''
class Struct:
    def __init__(_,rawdat) :
        _.__dict__ = rawdat
        for k,v in rawdat.items() :
            if isinstance(v,dict):
                _.__dict__[k] = Struct(v)
            if isinstance(v,list):
                if all(type(x) is dict for x in v):
                    _.__dict__[k] = [Struct(i) for i in v]
                else:
                    _.__dict__[k] = v

