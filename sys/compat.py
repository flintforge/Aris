'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:21>
Released under the MIT License
'''

import sys,os

compat_platform = sys.platform
if "bsd" in compat_platform:
    compat_platform = "linux-compat"

def _file(f):
    path = f.split('/')
    return os.path.join(*path)
