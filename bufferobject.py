
from OpenGL.GL import glGenBuffers, glBindBuffer, glBufferData,\
    glDrawElements, GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER,\
    GL_STATIC_DRAW, GL_UNSIGNED_INT, GL_QUADS

from numpy import hstack
from ctypes import c_float, c_uint, c_void_p, sizeof
uint_size  = sizeof(c_uint)


class BufferObject :
    """ An interleavded ready to go buffer for UNindexed index"""

    def __init__(self,args):


        # assume all elements have correct size

        self.nElement = len(args[0])
        print('new buffer : %i elements' % self.nElement)

        # interleave data
        data = hstack(args).flatten()

        self.indexBuffer = glGenBuffers(1)
        self.dataBuffer = glGenBuffers(1)

        indices_buffer = (c_uint*self.nElement)(*list(range(self.nElement)))
        data_buffer = (c_float*len(data))(*data)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBuffer )
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices_buffer, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.dataBuffer)
        glBufferData(GL_ARRAY_BUFFER, data_buffer, GL_STATIC_DRAW)

        del indices_buffer
        del data_buffer

    def bind(self):
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.indexBuffer )
        glBindBuffer(GL_ARRAY_BUFFER, self.dataBuffer)

    def render(self,mode=GL_QUADS):
        glDrawElements(mode,self.nElement, GL_UNSIGNED_INT,c_void_p(0))

