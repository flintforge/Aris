'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''

from OpenGL.GL import glGenBuffers, glBindBuffer, glBufferData,\
    glDrawElements, GL_ARRAY_BUFFER, GL_ELEMENT_ARRAY_BUFFER,\
    GL_STATIC_DRAW, GL_UNSIGNED_INT, GL_TRIANGLES, GL_TRIANGLE_STRIP
from numpy import hstack
from ctypes import c_float, c_uint, c_void_p, sizeof
all = ['IndexedBuffer']

#uint_size  = 

class IndexedBuffer :
    """ An interleavded ready to go buffer for indexed elements"""

    def __init__(self,index,args):
        """
        setup two buffers : one for the element index,
        the other with the actual data
        """
        # assume all index are triangles or quads
        self.nElement = len(index)

        # interleave data
        data = hstack(args).flatten()

        self.indexBuffer = glGenBuffers(1)
        self.dataBuffer = glGenBuffers(1)

        indices_buffer = (c_uint*self.nElement)(*index)
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

    def render(self,mode=GL_TRIANGLES):
        ''' at once '''
        glDrawElements(mode, self.nElement, GL_UNSIGNED_INT,c_void_p(0))


    def renderEach(self,mode=GL_TRIANGLES):
        """ per triangle rendering """
        offset = 0
        for size in self.sizes:
            glDrawElements(GL_TRIANGLE_STRIP,
                           size, GL_UNSIGNED_INT,
                           c_void_p(offset))
            offset += size * sizeof(c_uint)


