'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2014-02-189 15:52:50>
Released under the MIT License

A quick and lazy one.
a correct solution is to only update the texcoords,
not to move the GL_TEXTURE matrix local state
'''

from pyglet.gl import *

class ScrollingTex():

    def __init__(_, texture, dx=0.01, dy=-0.01, x=0,y=0, scaledTo=(1,1)):
        _.x = x
        _.y = y
        _.dx = dx
        _.dy = dy
        _.texture = texture
        _.width,_.height = scaledTo[0], scaledTo[1]
        _.id = texture.id
        _.tex_coords = [0,0,0,1,0,0,1,1,0,0,1,0]
        _.tex_coords[3] = _.tex_coords[6] = scaledTo[0]/_.texture.width
        _.tex_coords[7] = _.tex_coords[10] = scaledTo[1]/_.texture.height


    def update(_, dt):
        _.x += _.dx * dt
        _.y += _.dy * dt

    def bind(_, MATRIX_MODE=GL_MODELVIEW):
        glBindTexture(GL_TEXTURE_2D, _.texture.id)
        glMatrixMode(GL_TEXTURE)
        glTranslatef(_.x, _.y, 0)
        # restore
        glMatrixMode(MATRIX_MODE)

    def __enter__(_,MATRIX_MODE=GL_MODELVIEW):
        _.bind(MATRIX_MODE)

    def __exit__(_, exc_type, exc_value, traceback):
        glMatrixMode(GL_TEXTURE)
        glLoadIdentity()

class MultiScrollingTex():
    ''' one tex, multiple position/orientations '''
    def __init__(_, tex_handle, P=[(0.01,-0.01,0)]):
        '''
        parameters : P[] = an array of tuples : [(dx,dy,r)]
        '''
        _.tex_handle = tex_handle
        _.n = n = len(P)
        _.x = n*[0]
        _.y = n*[0]
        _.dx = [ p[0] for p in P]
        _.dy = [ p[1] for p in P]
        _.r = [ p[2] for p in P]

    def update(_, dt):
        _.x = [ _.x[i] + _.dx[i] * dt for i in range(_.n) ]
        _.y = [ _.y[i] + _.dy[i] * dt for i in range(_.n) ]

    def bind(_):
        _.tex_handle.bind()

    def animate(_,i):
        glMatrixMode(GL_TEXTURE)
        glRotatef(_.r[i],0,0,1)
        glTranslatef(_.x[i], _.y[i], 0)
        #glMatrixMode(GL_MODELVIEW)
