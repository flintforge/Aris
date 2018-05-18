'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''

from linalg import quaternion as _q
from linalg import matrix as _m
from linalg import vector as _v
from math import sin, cos, tan
from OpenGL.GL import glFrustum, glOrtho
# from states import State

DEGREE_TO_RADIAN = 0.01745329251994329576

class Camera(object):
    '''
    a camera : either a simple MVP matrix for rotation and translation
    or a 'targeting' camera, wich keep its aiming even when translated,
    while still rolling.
    '''

    def __init__(_, ratio=1, cameratype='FREE'):
        super(Camera, _).__init__()

        _.ratio = ratio  # window proportionnal aspect
        _.position = [0, 0, 0]
        # for target mode
        _.lookAt = [0, 0, -1]
        _.up = [0, 1, 0]
        # for ortho mode

        _.near_clip = 0.1
        _.far_clip = 2000
        _.fov = 45
        _.roll = 0
        _.matrix = _m.identity()
        _.rotation = _q.quaternion()
        _.speed = 0.5

        _.V = _m.identity()  # kept for PV inner computation
        ''' need a state switcher over dict
        CameraType = Enum('CameraType','FREE TARGET ORTHOGRAPHIC')
        cameraState = State(['camera_type'])
        cameraState.states('camera_type',CameraType)
        '''
        _.types = {'FREE': _.camera_free,
                      'ORTHOGRAPHIC': _.camera_ortho,
                      'TARGET': _.camera_target}

        _.setMode(cameratype)

    def setMode(_, mode):
        _.pfunc = _.types[mode]

    def update(_, width, height):

        _.width, _.height = width, height
        _.aspectRatio = max(width, height) / min(width, height)
        nc, fc, fov, ar = _.near_clip, _.far_clip, _.fov, _.aspectRatio

        # udpate free mode
        half_lens = nc * (tan(fov * DEGREE_TO_RADIAN / 2.))
        apperture_size = half_lens * ar
        _.frustum = (-apperture_size, apperture_size,
                        -half_lens, half_lens,
                        nc, fc)

        # update ortho mode also
        radius = .5 * min(width, height)
        w, h = width / radius, height / radius
        _.ortho = (-w, w, -h, h, -1, 1)

    def updateProjMat(_):

        # projection matrix. double check please
        fd = 1. / tan(_.fov * DEGREE_TO_RADIAN / 2.)
        nc, fc, fov, ar = _.near_clip, _.far_clip, _.fov, _.aspectRatio

        a1 = (fc + nc) / (nc - fc)
        a2 = 2. * fc * nc / (nc - fc)

        fd1 = fd / _.aspectRatio

        _.projmat = [[fd1, 0,    0,    0],
                        [0,   fd,   0,    0],
                        [0,   0,    a1,  -1],
                        [0,   0,    a2,   0]]

    def execute(_):
        _.pfunc()

    def camera_ortho(_):
        glOrtho(*_.ortho)

    def camera_free(_):
        glFrustum(*_.frustum)

    def camera_target(_):
        raise

    def translate(_, x, y, z):
        _.position[0] += x
        _.position[1] += y
        _.position[2] += z
        _.matrix[0][3] = _.position[0]
        _.matrix[1][3] = _.position[1]
        _.matrix[2][3] = _.position[2]
        # _.compute()

    def arcball(_, p0, p1):
        ''' set the rotation only according to the arcball'''
        _.rotation = _q.product(
            _.rotation, _q.arcball(*p0), _q.arcball(*p1))
        _.matrix = _q.matrix(_.rotation)
        '''
        matrix[0][3] = _.position[0]
        matrix[1][3] = _.position[1]
        matrix[2][3] = _.position[2]
        '''
        # _.compute()

    def setTranslation(_):
        _.matrix[0][3] = _.position[0]
        _.matrix[1][3] = _.position[1]
        _.matrix[2][3] = _.position[2]

    def compute(_):
        ''' OPTIMIZATION: factorize directly all computations in here'''
        #_.camera = _m.mul(_.camera, _m.translate(dx/100,dy/100,0))
        _.matrix = _m.mul(_m.translate(*_.position),
                             _q.matrix(_.rotation))

    def target_orientation(_):

        up = (sin(roll * DEGREE_TO_RADIAN),
              cos(roll * DEGREE_TO_RADIAN), 0)
        '''
         * the following section of code is the sgl version of
         *
         * gluLookAt(   position.x, position.y, position.z,
         *              lookAt.x, lookAt.y, lookAt.z,
         *              up.u, up.v, up.w )
        '''

        forward = _v.normalize(_v.sub(_.lookAt, _.position))
        side = _v.normalize(_v.cross(forward, up))
        up = _v.cross(side, forward)

        _.matrix = [[side[0],     side[1],     side[2],    position.x],
                       [up[0],       up[1],       up[2],      position.y],
                       [-forward[0], -forward[1], -forward[2], position.z],
                       [0, 0, 0, 1]]

    def lookB(_, phi, theta, psi):
        ''' spherical coordinates
        only time with euler angles, promise '''
        _.lookAt = (sin(psi) * cos(theta),
                       sin(psi) * sin(theta),  # =x tan(theta)
                       cos(theta))

        forward = _v.normalize(_v.sub(_.lookAt, _.position))
        side = _v.normalize(_v.cross(forward, _.up))
        up = _v.cross(side, forward)

        matrix = [[side[0],     side[1],     side[2],    _.position[0]],
                  [up[0],       up[1],       up[2],      _.position[1]],
                  [-forward[0], -forward[1], -forward[2], _.position[2]],
                  [0, 0, 0, 1]]
        return matrix

    def look(_, up):
        forward = _v.normalize(_v.sub(_.lookAt, _.position))
        side = _v.normalize(_v.cross(forward, up))
        up = _v.cross(side, forward)

        matrix = [[side[0],     side[1],     side[2],    _.position[0]],
                  [up[0],       up[1],       up[2],      _.position[1]],
                  [-forward[0], -forward[1], -forward[2], _.position[2]],
                  [0, 0, 0, 1]]
        return matrix

    def rotationIPV(_, view):
        ''' Inverse Projection Matrix
        in usage for a skybox cam
        since glFrustum isn't called here,
        compute PV from an other given mat,
        discard translation and inverse
        '''

        PV = _m.mul(_m.transpose(_.projmat), view)

        # PV[0][3]=PV[1][3]=PV[2][3]=0
        #PV[3] = [0,0,0,1]
        _.matrix = _m.inverse(PV)
        #_.matrix[3] = [0,0,0,1]
        # _.matrix[0][3]=_.matrix[1][3]=_.matrix[2][3]=0


    def pickRay(_, x, y):
        s = 2.0 * tan(_.fov / 2.0)
        pickDirection = (x * s, y * s, -1.0)
        return _v.normalize(pickDirection)

