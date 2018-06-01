'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-06-01 02:12:02>
Released under the MIT License
'''
from OpenGL.GL import *

class RTT :

    def __init__(_):

        _.active = True
        _.FBO, _.RTTex = None,None
        _.shader = None,

    def setup(_, width, height, internalformat=GL_RGBA8, pixformat=GL_RGBA) :
        '''
        specify GL_RGBA & GL_RGBA8 for a transparent FBO
        '''
        _.samples = glGetInteger(GL_SAMPLES)

        if not glGenFramebuffers:
            return False


        _.FBO = glGenFramebuffers(1)

        #'''
        glBindFramebuffer(GL_FRAMEBUFFER, _.FBO)
        depthbuffer = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, depthbuffer)
        glRenderbufferStorage(GL_RENDERBUFFER, GL_DEPTH_COMPONENT24, width, height)
        glFramebufferRenderbuffer( GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_RENDERBUFFER, depthbuffer)
        '''
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, _.FBO)
        rb_color, rb_depth_stencil = glGenRenderbuffers(2)
        glBindRenderbuffer(GL_RENDERBUFFER, rb_color)
        #glRenderbufferStorageMultisample(GL_RENDERBUFFER, _.samples, GL_RGBA, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_RENDERBUFFER, rb_color)
        glBindRenderbuffer(GL_RENDERBUFFER, rb_depth_stencil)
        glRenderbufferStorageMultisample(GL_RENDERBUFFER, _.samples, GL_DEPTH_STENCIL, width, height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER, GL_DEPTH_STENCIL_ATTACHMENT, GL_RENDERBUFFER, rb_depth_stencil)
        #'''


        glActiveTexture(GL_TEXTURE0)
        _.RTTex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, _.RTTex)
        #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
        #glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexImage2D( GL_TEXTURE_2D, 0, internalformat,
                      width, height, 0, pixformat,
                      GL_UNSIGNED_INT,
                      None )# no data transferred

        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, _.RTTex,
                                  0 ) # mipmap level
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        assert status == GL_FRAMEBUFFER_COMPLETE, status
        # ready, unbind
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        _.w,_.h = width,height


    def __enter__(_):
        glBindFramebuffer(GL_FRAMEBUFFER, _.FBO)
        glClearColor(0,0,0,0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    def __exit__(self, *args):
        pass



    def blit(_, in_drawFB=0):
        # alpha chan ?
        glBindFramebuffer(GL_DRAW_FRAMEBUFFER, in_drawFB.FBO)
        glBindFramebuffer(GL_READ_FRAMEBUFFER, _.FBO)
        glBindTexture(GL_TEXTURE_2D, _.RTTex)
        #glBindTexture(GL_TEXTURE_2D, _.RTTex)
        # assume same size for now
        glBlitFramebuffer(0, 0, _.w, _.h, 0, 0, _.w, _.h,GL_COLOR_BUFFER_BIT | GL_STENCIL_BUFFER_BIT, GL_NEAREST)
