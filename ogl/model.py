'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:43>
Released under the MIT License
'''
import numpy as np
from linalg import vector as _v
from bufferobject import BufferObject
from indexedbuffer import IndexedBuffer
from linalg import matrix as _m
from linalg import quaternion as _q
#from elipsoid import Elipsoid

class Model(object):
    """docstring for ClassName"""

    def __init__(_, mesh, tex_coords, name=''):
        _.mesh = mesh
        _.tex_coords = tex_coords
        _.name = name
        # todo
        _.matrix = _m.identity()
        _.rotation = _q.quaternion()
        _.position = 0, 0, 0
        _.createBuffers()

    def createBuffers(_):
        elements = (_.mesh._vertices, _.tex_coords,
                    _.mesh._normals, _.mesh._colors)
        # elements = ( x for x in elements if x is not None)
        elements = list(x for x in elements if x is not None)
        _.buffer = IndexedBuffer(_.mesh._faces, elements)  # BufferObject(elements)

    def render(_):
        _.buffer.render()

    ''' mobile objects definition. to generalize '''

    def setPosition(_, x, y, z):
        _.position = x,y,z
        _.matrix[0][3] = x
        _.matrix[1][3] = y
        _.matrix[2][3] = z

    def translate(_, x, y, z):
        _.matrix = _m.add(_.matrix, _m.translate(x, y, z))

    def rotate(_, x, y, z):
        _.matrix = _m.add(_.matrix, _m.rotate(x, y, z))

    def scale(_, x):
        _.scale = x
        # into the matrix please


def rgb(x, y, z):
    return abs(x), abs(y), abs(z)


class Mesh(object):

    def __init__(_, vertices, faces, normals=None, colors=None):
        _._vertices = vertices
        _._faces = faces
        _._normals = normals
        _._colors = colors
        # bouding elipse

    def computeNormals(_):
        # quad base or tri base?
        pass

    @classmethod
    def computeBBox(cls, mesh):
        """ get the min and max x,y,z coordinates"""

        pass

    def computeBEllipse(_):
        minaxis = _._vertices.min(axis=0)
        maxaxis = _._vertices.max(axis=0)
        centeraxis = maxaxis+minaxis

        return Elipsoid(centeraxis,maxaxis)

    def merge(_,mesh):
        _._vertices += mesh.vertices
        _._faces += mesh.faces
        _._normals += mesh.normals
        _._colors += mesh.colors


def vertexAndNormalsList(V, F):
    '''
    one normal per faces = one normal for each distinct vertices
    no shared verts. Gouraud Shading, diamond sharp edges

    the unormalized normals list, indexed on the vertex list
    unormalized = relative to the surface of the face.
    check the influence of the face size on the illumination model
    '''

    vertices = np.ndarray((len(F) * 3, 3), dtype=np.float32)
    normals = np.ndarray((len(F) * 3, 3), dtype=np.float32)

    x = 0
    for f in F:
        p0, p1, p2 = [V[f[y]] for y in range(3)]
        n = _v.cross(_v.vector(p0, p1), _v.vector(p0, p2))
        for i in range(3):
            vertices[x] = V[f[i]]  # flatten / recopy the vertex
            # the three vertex hold the same normal value
            normals[x] = _v.div(_v.mag(n), n)
            x += 1

    return vertices, normals


def IndexedNormals(V, F):
    '''
    Keep the face index, and provide one normal per vertex
    '''
    # normals = np.ndarray((len(V)*3,3), dtype=np.float32)
    normals = [[] for x in range(len(V))]
    A = [[] for x in range(len(V))]
    # normals = np.ndarray((len(F)*3,3), dtype=np.float32)
    x = 0
    for f in F:
        p0, p1, p2 = [V[f[x]] for x in range(3)]
        n = _v.cross(_v.vector(p0, p1), _v.vector(p0, p2))
        for i in range(3):  # in triangle
            # print (f[i] , n)
            # normals[x].append(n)  # append the face normal
            # normals[x].append(f[i]) # keep the vertex index
            normals[f[i]].append(n)  # would index the normal by face
            # compute the adjacency list while we are in
            A[f[i]] += [fa for fa in f if fa != f[i] and fa not in A[f[i]]]
            x += 1

    for i, n in enumerate(normals):
        # print(n,len(n),_v.sum(*n), _v.div(float(len(n)),_v.sum(*n)))
        # weighted by the number of face = wrong
        normals[i] = _v.div(float(len(n)), _v.sum(*n))
        # print('>',normals[i])

    # print('#',A)
    # print('//',normals, len(normals))
    return normals


def adjacencyList(V, F):
    '''
    compute the adjacency list of every vertex. usage ?
    '''
    A = [[] for x in range(len(V))]

    for v in range(len(V)):  # iterate all vertex index
        for f in F:         # go through every faces index
            if v in f:      # is this v index is in it
                A[v] += [fa for fa in f if fa != v and fa not in A[v]]
                # add all other faces to the adjacency
    return A


def Import3dsList(L):
    return [Import3ds(m) for m in L]


def Import3ds(Name, V, F, T=None):

    # vertices, normals = vertexAndNormalsList(V,F)

    # A = adjacencyList(V,F)
    # N = IndexedNormals(V,F)
    ''' per vertex mean normal '''
    '''
    for (i,a) in enumerate(A) : # for every adjacency list / vertex
        print( list(normals[x] for x in a ))
    '''
    '''
    N=[None]*len(V)
    for i,v in enumerate(V) :
        N[i] = _v.normalize(v)
    '''
    N = IndexedNormals(V, F)
    # V = np.ndarray((len(vertices),3) ,dtype=np.float32,order='C')
    F = list(F.flatten())
    # mesh = Mesh(vertices, normals, colors)

    mesh = Mesh(V, F, N, V)

    if T is None:
        print('NO tex Coords')
    texcoords = T if T is not None else np.delete(V, 2, 1)
    # texcoords = [ [t[0], t[1], 0 ] for t in T ] if T is not None else V
    model = Model(mesh, texcoords)
    return model


def debugNormalsBuffer(mesh):
    V, N = mesh.vertices, mesh.normals
    normals = []
    for v, n in zip(V, N):
        normals.append(v)
        v2 = [v[i] + n[i] for i in range(3)]
        normals.append(v2)
    return BufferObject([normals])


"""
to debug normals
with _.neutral:
    _.normals.bind()
    _.neutral.activateVertexAttribs()
    _.normals.render(mode=GL_LINES)
"""


if __name__ == '__main__':
    from parse3ds import parse3ds
    m = parse3ds('./3ds/vyper3R.3ds')
    if type(m) is list:
        models = Import3dsList(m)
    else:
        model = Import3ds(*m)


