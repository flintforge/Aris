'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:43>
Released under the MIT License
'''
import numpy as np
from OpenGL.GL import *
from pyglet import image
import logging
logger = logging.getLogger("clogger.%s" % __name__)


"""
todo :
image format
- alpha and greyscales : luminance+alpha
- channels management

more procedural pixel processing
Noise, lattices, glows
"""


class Dim3(object):
    """
    width, heigh, depth, size
    """

    def __init__(_, dim):
        _.w = dim[0]
        _.h = dim[1]
        _.d = dim[2]
        _.size = _.h * _.w * _.d


class PixelBuffer(object):
    """
    - dim=3 * [None], data=None, planes=4
    - png data accepted. binary
    possible optimisation :
    - check the 'data' parameter type.
    - if function, call, to avoir the copy

    semantic pb here :
     should we have planes for level in a 3d stack ?
     or declare depth as in depth color ?
    """

    def __init__(_, dim=3 * [None], data=None, planes=1):
        super(PixelBuffer, _).__init__()
        _.id = glGenBuffers(1)
        _.width, _.height, _.depth = dim
        _.planes = planes
        _.size = _.width * _.height * _.planes
        _.data = data
        logger.info('new Pixel Buffer %i %ix%i' % (_.size,_.width,_.height))

        with _: _.bufferdata #

    def __enter__(_):
        _.bind()
        #_.bufferdata()

    def bind(_): glBindBuffer(GL_PIXEL_UNPACK_BUFFER, _.id)

    def __exit__(_, exc_type, exc_value, traceback):
        glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)

    def bufferdata(_):
        glPixelStorei(GL_PACK_ALIGNMENT,1) # keep 4 by default if it's rgba
        glPixelStorei(GL_PACK_ROW_LENGTH, _.width)
        glBufferData(GL_PIXEL_UNPACK_BUFFER,_.size,_.data,GL_STREAM_DRAW)
        glPixelStorei(GL_PACK_ALIGNMENT, 4)
        glPixelStorei(GL_PACK_ROW_LENGTH, 0)

    def read(_,data):
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        glPixelStorei(GL_PACK_ROW_LENGTH, _.width)
        glBufferSubData(GL_PIXEL_PACK_BUFFER, 0, _.size, data)

    def __del__(_):
        """ cleanup the buffer """
        glDeleteBuffers(1, [_.id])
        del _.data


class PixelGenerator():
    """
    the single function looks better
    """
    @classmethod
    def Dim3(cls, func, w, h, d):
        """ 3D pix buffer factory """
        data = b''.join(func(i, j, k) for i in range(w)
                        for j in range(h)
                            for k in range(d))
        return PixelBuffer((w, h, d), data)


def PixelGeneration(func, w, h, d=1):
    """ 3D pix buffer factory """
    data = b''.join(func(i, j, k) for i in range(w)
                    for j in range(h)
                    for k in range(d))
    return PixelBuffer((w, h, d), data)


def chessboard(i, j, k, white=b'\xff\xff\xff\xff',
               black=b'\x00\x00\x00\xff'):
    return black if (i + j + k) % 2 == 0 else white


def punch_holes3d(i, j, k, opaque=b'\xff\xff\xff\xff',
                  transparent=b'\xff\xff\xff\x00'):
    return opaque if (i + j + k) % 2 == 0 else transparent


# will slice the axes modula . holes with i*j*k, etc
def punch_lines(i, j, k, opaque=b'\xff\xff\xff\xff',
                transparent=b'\xff\xff\xff\x00'):
    return opaque if (i) % 2 == 0 else transparent


def random_data_points(w, h):
    return PixelBuffer(w, h, np.array(.2 * rdn.randn(100000, 2), dtype=np.float32))



COLORS = {
    'RGB':1,
    'RGBA':4
}

def Image(file):
    img = image.load(file)
    imgdata = img.get_image_data()
    pixbuf = PixelBuffer((img.width, img.height, COLORS[imgdata.format]), imgdata.data)
    return pixbuf


'''
def Image2(file):
    """ use the png reader
    """
    if file.endswith('.png'):
        # can't read it flat as it is reversed
        w, h, data, infos = png(file).read()

        # it's backward. revert it back
        # data = reversed(list(data))

        data = list(itertools.chain(*data))
        data = struct.pack(len(data) * 'B', *data)

        pixbuf = PixelBuffer((w, h, 1), data)

        logger.debug(fil + infos)
        if infos['greyscale']:
            pixbuf.planes = 1
        if infos['alpha']:  # unless there's only a alpha channel...
            pixbuf.planes += 1

        return pixbuf

    else:
        raise Exception('sorry i read only png for now')
'''

if __name__ == '__main__':
    Image('./earth.png')
