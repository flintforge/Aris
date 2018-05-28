'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''
import itertools

class Cycler:
    def __init__(_, data):
        _.data = data
        _.iterator = itertools.cycle(data)
        _.jump_to_previous = len(data) - 2

    def next(_):
        return _.data[next(_.iterator)]

    def previous(_):
        prev = itertools.islice(_.iterator, _.jump_to_previous, None)
        return _.data[next(prev)]

    def __getitem__(_,x):
        return _.data[x]
