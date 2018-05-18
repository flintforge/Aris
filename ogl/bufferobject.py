'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:43>
Released under the MIT License
'''

from OpenGL.GL import glGenBuffers, glBindBuffer, glBufferData,\
    glDrawElements, GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER,\
    GL_STATIC_DRAW, GL_UNSIGNED_INT, GL_QUADS

from numpy import hstack
from ctypes import c_float, c_uint, c_void_p, sizeof
uint_size  = sizeof(c_uint)


class BufferObject :
    """ An interleavded ready to go buffer for UNindexed index"""

    def __init__(__,args):


        # assume all elements have correct size

        __.nElement = len(args[0])
        print('new buffer : %i elements' % __.nElement)

        # interleave data
        data = hstack(args).flatten()

        __.indexBuffer = glGenBuffers(1)
        __.dataBuffer = glGenBuffers(1)

        indices_buffer = (c_uint*__.nElement)(*list(range(__.nElement)))
        data_buffer = (c_float*len(data))(*data)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, __.indexBuffer )
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_buffer, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, __.dataBuffer)
        glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)

        del indices_buffer
        del data_buffer

    def bind(__):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, __.indexBuffer )
        glBindBuffer(GL_ARRAY_BUFFER, __.dataBuffer)

    def render(__,mode=GL_QUADS):
        glDrawElements(mode,__.nElement, GL_UNSIGNED_INT,c_void_p(0))

