'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-27 00:36:24>
Released under the MIT License
'''

from OpenGL.GL import *
from pixelbuffer import Image
from pyglet import image
from compat import _file



def blit(tex,x=0,y=0,z=0):
    # using pyglet.image.texture
    glBindTexture(GL_TEXTURE_2D, tex.id)
    t = tex.tex_coords
    x2, y2 = x+tex.width, y+tex.height
    array = (GLfloat * 32)(
        t[0], t[1], t[2],  1.,
        x,    y,    z,     1.,
        t[3], t[4], t[5],  1.,
        x2,   y,    z,     1.,
        t[6], t[7], t[8],  1.,
        x2,   y2,   z,     1.,
        t[9], t[10], t[11],1.,
        x,    y2,   z,     1.)

    glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
    glInterleavedArrays(GL_T4F_V4F, 0, array)
    glDrawArrays(GL_QUADS, 0, 4)
    glPopClientAttrib()



def blitbound(
        tex,
        tex_coords=(0,0,0,1,0,0,1,1,0,0,1,0),
        x=0,y=0,z=0):
    # using pyglet.image.texture
    t = tex.tex_coords
    x2, y2 = x+tex.width, y+tex.height
    array = (GLfloat * 32)(
        t[0], t[1], t[2],  1.,
        x,    y,    z,     1.,
        t[3], t[4], t[5],  1.,
        x2,   y,    z,     1.,
        t[6], t[7], t[8],  1.,
        x2,   y2,   z,     1.,
        t[9], t[10], t[11],1.,
        x,    y2,   z,     1.)

    glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
    glInterleavedArrays(GL_T4F_V4F, 0, array)
    glDrawArrays(GL_QUADS, 0, 4)
    glPopClientAttrib()


def _blit(tex,w,h,tx,ty,x=0,y=0,z=0):
    # using pyglet.image.texture
    glBindTexture(GL_TEXTURE_2D, tex)
    x2, y2 = x+w, y+h
    array = (GLfloat * 32)(
        0,   0, 0 , 1,  x , y2     ,  0,1,
        tx,  0, 0 , 1,  x2, y     ,  0,1,
        tx,  ty,0 , 1,  x2, y2   ,  0,1,
        0,   ty,0 , 1,  x , y2  ,  0,1)

    glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
    glInterleavedArrays(GL_T2F_V3F, 0, array)
    glDrawArrays(GL_QUADS, 0, 4)
    glPopClientAttrib()



"""
1,2,3D Textures classes

really need to discard alpha channel for maps who don't have
"""

class Texture(object):
    '''
    the GL_ACTIVE_TEXTURE when multitexturing
    with glActiveTexture(GL_TEXTURE0+i)
    where i is Texture.active_unit
    '''
    active_unit = 0
    count = 0

    def __init__(_, file=None, generator=None):
        _.id = glGenTextures(1)
        Texture.count += 1 # not thread safe
        _.unit = Texture.active_unit
        if file:
            _.create(Image(file))
        elif generator:
            _.create(PixelGenerator(generator))
        else:
            _.create(PixelGenerator(chessboard))

    def fromFile(_,file) :
        _.create(Image(file))

    def bind(_):
        glBindTexture(_.type, _.id)


class Texture1D(Texture):

    def __init__(_):
        ''' a 1D texture. pixbuf must be a line preferably'''
        Texture.__init__(_)
        _.type = GL_TEXTURE_1D
        _.create(pixbuf)

    def create(_,pixbuf):
        glBindTexture(GL_TEXTURE_2D, _.id)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        with pixbuf:
            glTexImage1D(GL_TEXTURE_1D, 0, GL_RGBA,
                         pixbuf.width,
                         0, GL_RGBA, GL_UNSIGNED_BYTE,
                         None)
        #pixbuf.data) no data data, PBO managed


class Texture2D(Texture):

    def __init__(_,file=None):
        _.type = GL_TEXTURE_2D
        Texture.__init__(_, file)
        #_.width,_.height = pixbuf.width, pixbuf.height,

    def create(_,pixbuf):
        glBindTexture(_.type, _.id)
        glTexParameter(_.type, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(_.type, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        #print(pixbuf.width, pixbuf.height)
        with pixbuf :
            _.width, _.height = pixbuf.width, pixbuf.height
            glTexImage2D(_.type, 0, GL_RGBA,
                         pixbuf.width,pixbuf.height,
                         0, GL_RGBA, GL_UNSIGNED_BYTE,
                         None)



class Texture3D(Texture):

    def __init__(_, file=None):
        _.type = GL_TEXTURE_3D
        Texture.__init__(_,file)

    def create(_, pixbuf, filtermode=GL_LINEAR):
        glBindTexture(GL_TEXTURE_3D, _.id)
        glTexParameter(GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameter(GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        with pixbuf :
            glTexImage3D(GL_TEXTURE_3D, 0, GL_RGBA,
                         pixbuf.width, pixbuf.height, pixbuf.depth,
                         0, GL_RGBA, GL_UNSIGNED_BYTE,
                         None)

        # pixbuf is automatically destroyed afterward


class Tex :
    def __init__(_,file):
        try:
            _.load(file)
        except FileNotFoundError:
            _.load(_file('GFX/missing.png'))

    def load(_,file):
        img = image.load(file)
        _.img = img
        _.tex = img.get_texture()
        print(_.tex)
        _.id = img.texture.id
        _.width = img.texture.width
        _.height = img.texture.height
        print('new TEX', _.id, _.width, _.height, file)

    def blit(_,x,y): blit(_,x,y)


