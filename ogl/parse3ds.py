'''
    Description: This is a 3DS file parser,
    it produces list of quadruplet :
    [ name, Vertex list, faces list, uv coordinates ]
    for each models in the file

    License: AGPLv3, see LICENSE for more details
    Author: 2011 Florian Boesch <pyalot@gmail.com>
    Updated: 2016 Phil Estival <𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵 @𝓕𝓻𝓮𝓮.𝓯𝓻>

    Helpful Links:
        http://en.wikipedia.org/wiki/.3ds
        http://www.spacesimulator.net/wiki/index.php?title=Tutorials:3ds_Loader
        http://www.martinreddy.net/gfx/3d/3DS.spec
        http://faydoc.tripod.com/formats/3ds.htm

    the name of the object can be used, to declare special patches,
    such as light sources or particles emmiter for instance.

TODO :
- multiple objects
- light sources
'''

from struct import unpack
from vector import Vec3
import numpy as np
from ansiprint import warning
import debuglog
logger = debuglog.init(__name__)

class Data:
    size = 0

    def __init__(self, parent, data):
        self.parent = parent

    def __repr__(self):
        return self.__class__.__name__


class Main(Data):
    pass


class Editor(Data):
    pass


class Object(Data):

    def __init__(self, parent, data):
        self.parent = parent
        zero_index = data.find(b'\0')
        self.name = data[:zero_index]
        self.size = zero_index + 1

    def __repr__(self):
        return '%s %s' % (self.name, self.size)


class Mesh(Data):
    pass

# np util
# try different solutions if performance becomes a requirement :
# http://stackoverflow.com/questions/16970982/find-unique-rows-in-numpy-array
# http://stackoverflow.com/questions/11528078/determining-duplicate-values-in-an-array


def unique_rows(a):
    a = np.ascontiguousarray(a)
    unique_a = np.unique(a.view([('', a.dtype)] * a.shape[1]))
    return unique_a.view(a.dtype).reshape((unique_a.shape[0], a.shape[1]))


def unique(a):
    diff = np.diff(a, axis=0)
    ui = np.ones(len(a), 'bool')
    ui[1:] = (diff != 0).any(axis=1)
    return a[ui]

# return a mask indicating unique elements


def dup_mask(a):
    m = np.ones(a.shape[0], dtype=bool)
    m[np.unique(a.view([('', a.dtype)] * a.shape[1]),
                return_index=True)[1]] = False
    return m


def indicesOfPreviouslyMet(A):
    # str the uplet as footprint
    B = [str(x) for x in A]
    vals, inverse, count = np.unique(
        B, return_inverse=True, return_counts=True)
    idx_vals_repeated = np.where(count > 1)[0]
    # print(idx_vals_repeated)
    #vals_repeated = vals[idx_vals_repeated]
    rows, cols = np.where(inverse == idx_vals_repeated[:, np.newaxis])
    _, inverse_rows = np.unique(rows, return_index=True)
    res = np.split(cols, inverse_rows[1:])
    return res


class Vertices(Data):

    def __init__(self, parent, data):
        self.parent = parent
        count = unpack('H', data[:2])[0]
        data = data[2:]
        self.vtx = []
        vtx = np.ndarray(shape=(count, 3), dtype=np.float32, order='C')

        x, y, z = unpack('fff', data[:3 * 4])
        data = data[3 * 4:]
        vtx[0] = (x, y, z)
        for i in range(1, count):
            x, y, z = unpack('fff', data[:3 * 4])
            # self.vtx.append((x,z,-y))
            vtx[i] = (x, y, z)
            data = data[3 * 4:]

        # collapse(method plz)
        self.size = 2 + count * 3 * 4

        # VERY carefull it does depends on the scale
        # let's assume our model is of scale 1 on a blender grid
        vtx = vtx.round(5)

        self.vertices = vtx

    def __repr__(self):
        return str(len(self.vertices)) + ' vertices'


class Faces(Data):

    def __init__(self, parent, data):
        self.parent = parent
        count = unpack('H', data[:2])[0]  # total polygons in object (numpoly)
        data = data[2:]
        #self.f = []
        # remove the flag later
        self.faces = np.ndarray((count, 3), order='C', dtype='uint32')

        for i in range(count):
            j = i + 1
            # discard flags
            # self.faces[i] = unpack('HHHH', data[i*4*2:j*4*2])

            v1, v2, v3, flags = unpack('HHHH', data[i * 4 * 2:j * 4 * 2])
            self.faces[i] = (v1, v2, v3)
            #self.f.append((v1, v2, v3, flags))
            # what to do with the flag ?
        self.size = 2 + count * 4 * 2  # bytes

        b = unique_rows(self.faces)
        if len(b) != len(self.faces):
            logger.warning('Warning! dup faces! %i' % len(self.faces) - len(b))

    def __repr__(self):
        return str(len(self.faces)) + ' faces '


class FaceMaterial:

    def __init__(self, parent, data):
        self.parent = parent
        zero_index = data.find(b'\0')
        self.name = data[:zero_index]
        data = data[zero_index + 1:]
        count = unpack('H', data[:2])[0]
        data = data[2:]
        # todo get indices
        self.faces = []
        for i in range(count):
            face_index = unpack('H', data[:2])[0]
            data = data[2:]
            self.faces.append(face_index)
        self.size = zero_index + 1 + 2 + count * 2

    def __repr__(self):
        return '%s %s' % (self.__class__.__name__, self.name)


class Texcoords(Data):

    def __init__(self, parent, data):
        self.parent = parent
        count = unpack('H', data[:2])[0]
        data = data[2:]
        uv = np.ndarray((count, 2), order='C', dtype='float32')
        for i in range(count):
            x, y = unpack('ff', data[:8])
            data = data[8:]
            uv[i] = [x, y]

        self.size = 2 + count * 2 * 4
        self.texcoords = uv.round(5)

    def __repr__(self):
        return str(len(self.texcoords)) + ' uv'


class Matrix(Data):

    def __init__(self, parent, data):
        self.parent = parent
        self.size = 12 * 4
        r11, r21, r31, r21, r22, r23, r31, r32, r33, x, y, z = unpack(
            'f' * 12, data)
        self.rot = [r11, r21, r31, r21, r22, r23, r31, r32, r33]
        self.center = Vec3(x, z, -y)


class SmoothGroup(Data):

    def __init__(self, parent, data):
        self.size = len(data)
        self.parent = parent
        self.groups = []
        for i in range(len(parent.parent.data.faces)):
            group_id = unpack('i', data[:4])[0]
            self.groups.append(group_id)
            data = data[4:]


class Keyframer(Data):
    pass


class ObjectDescription(Data):
    pass


class ObjectHirarchy(Data):

    def __init__(self, parent, data):
        self.parent = parent
        zero_index = data.find(b'\0')
        self.name = data[:zero_index]
        data = data[zero_index + 1:]
        self.size = zero_index + 1 + 3 * 4
        self.hirarchy = unpack('H', data[4:6])[0]

    def __repr__(self):
        return '%s %s %i' % (self.__class__.__name__, self.name, self.hirarchy)


names = {
    0x4d4d: Main,
    0x3d3d: Editor,
    0x4000: Object,
    0x4100: Mesh,
    0x4110: Vertices,
    0x4120: Faces,
    0x4140: Texcoords,
    0x4160: Matrix,
    0x4130: FaceMaterial,
    0x4150: SmoothGroup,
    0xb002: ObjectDescription,
    0xb010: ObjectHirarchy,
}
skipped = {
    0x0000: 'NULL',
    0x0002: 'VERSION',
    0x0010: 'COLOR_FLOAT',
    0x0011: 'COLOR_24',
    0x0013: 'LIN_COLOR_F',
    0x0030: 'INT_PERCENTAGE',
    0x0031: 'FLOAT_PERCENTAGE',
    0x0100: 'MASTER_SCALE',
    0x1200: 'BACKGROUND_COLOR',
    0x3d3d: 'MESHDATA',
    0x3d3e: 'MESH_VERSION',
    0x4000: 'NAMED_OBJECT',
    0x4100: 'TRIANGLE_MESH',
    0x4110: 'POINT_ARRAY',
    0x4111: 'POINT_FLAG_ARRAY',
    0x4120: 'FACE_ARRAY',
    0x4130: 'MESH_MATERIAL_GROUP',
    0x4140: 'MESH_TEXTURE_COORDS',
    0x4150: 'MESH_SMOOTH_GROUP',
    0x4160: 'MESH_MATRIX',
    0x4d4d: 'MAGIC',
    0xa000: 'MATERIAL_NAME',
    0xa010: 'MATERIAL_AMBIENT',
    0xa020: 'MATERIAL_DIFFUSE',
    0xa030: 'MATERIAL_SPECULAR',
    0xa040: 'MATERIAL_SHININESS',
    0xa041: 'MATERIAL_SHIN2PCT',
    0xa050: 'MATERIAL_TRANSPARENCY',
    0xa052: 'MATERIAL_XPFALL',
    0xa053: 'MATERIAL_REFBLUR',
    0xa084: 'MATERIAL_SELF_ILLUM',
    0xa087: 'MATERIAL_WIRESIZE',
    0xa08a: 'MATERIAL_XPFALLIN',
    0xa100: 'MATERIAL_SHADING',
    0xa200: 'MATERIAL_TEXMAP',
    0xa300: 'MATERIAL_MAPNAME',
    0xafff: 'MATERIAL_ENTRY',
    0xb000: 'Keyframer',

}


def print_chunk(chunk, indent=0):
    logger.debug('%s%04X: %s' % ('  ' * indent, chunk.id, chunk.name))
    for child in chunk.children:
        print_chunk(child, indent + 1)


class Children(object):

    def __init__(self):
        self.list = []
        self.map = {}

    def add(self, child):
        name = child.name.lower()
        map = self.map
        self.list.append(child)
        if name in map:
            if isinstance(map[name], list):
                map[name].append(child)
            else:
                map[name] = [map[name], child]
        else:
            map[name] = child

    def __iter__(self):
        return iter(self.list)

    def __getitem__(self, key):
        if isinstance(key, str):
            return self.map[key]
        else:
            return self.list[key]

    def __getattr__(self, name):
        try:
            return self.map[name]
        except KeyError:
            logger.warning('warning, no %s' % name)


class Chunk:

    def __init__(self, parent, id, data):
        self.parent = parent
        self.id = id
        self.name = 'unknown'
        self.data = None
        self.children = Children()

        if id in names:
            self.data = names[id](self, data)
            self.name = self.data.__class__.__name__
            self.parse_chunks(data[self.data.size:])
        else:
            if id in skipped:
                self.name = skipped[id]
                logger.debug(skipped[id] + ' skipped')

    def parse_chunks(self, data):
        while data:
            id = unpack('H', data[:2])[0]
            length = unpack('i', data[2:6])[0]
            self.children.add(Chunk(self, id, data[6:length]))
            data = data[length:]


class File3Ds:

    @staticmethod
    def open(filename):
        data = open(filename, 'rb').read()
        return File3Ds(data)

    def __init__(self, data):
        self.data = data
        id = unpack('H', data[:2])[0]
        # length = unpack('i', data[2:6])[0]
        data = data[6:]
        self.main = Chunk(self, id, data)


def processDup(v, V, F):
    dup = dup_mask(V)
    logger.debug('process dup %i %i' % (len(v), len(V)))
    """
        compute the list of already met indices under the form :
        [0,2,3],[5,7,8] where x[0] is the first indice,
        and  the following are the further localized ones
        """
    mF = indicesOfPreviouslyMet(F)
    logger.debug('met:%s' % str(mF))
    # retain the list of met indices
    met = [x[0] for x in mF]

    logger.debug('dup mask %s' % str(dup))
    # compute the shift acccumulator
    # acc = np.add.accumulate(F)
    # patch the face index for the unique vtx array
    for f in F:
        for i in range(3):
            idx = met.index(f[i])
            # f[i] -= acc[f[i]]
    print(F)


def NVFT(obj):
    ''' return name, vertex, faces, uv from an obj '''
    mesh = obj.children.mesh
    faces = mesh.children.faces
    vertices = mesh.children.vertices
    texcoords = mesh.children.texcoords
    #matrix = mesh.children.matrix
    #center = matrix.data.center
    #groups = faces.children.smoothgroup.data.groups

    name = obj.data.name.decode()
    V = vertices.data.vertices
    F = faces.data.faces
    T = texcoords.data.texcoords if texcoords else None

    v = unique(V)
    logger.info('processing 3ds chunk : %s %s' % (obj.name, name))
    logger.debug('%i vertices' % len(V))

    if len(v) != len(V):
        logger.warning('%i dup vertex' % (len(V) - len(v)))
        # processDup(v,V,F)
    #logger.debug(V[0:6])
    logger.debug('vmax:%a' % V.max(axis=0))
    logger.debug('vmin:%a' % V.min(axis=0))
    logger.debug('vmean:%a' % V.mean(axis=0))

    if texcoords:
        logger.debug('%i UV' % len(T))
        logger.debug('max:%i' % max(T.max(0)))
        logger.debug('min:%i' % min(T.min(0)))

    #print(repr(faces.data))
    if texcoords:
        logger.debug(repr(texcoords.data))

    return name, V, F, T


def parse3ds(file):
    """
    returns a geometry
    """
    logger.info('parsing %s' % file)
    infile = File3Ds.open(file)
    # only one object

    OBJ = infile.main.children.editor.children.object

    if type(OBJ) is list:
        # there are several models, return a list
        models = []
        for obj in OBJ:
            models.append(NVFT(obj))
        return models

    else:  # return the tuple n,v,f,t
        return NVFT(OBJ)


if __name__ == '__main__':

    testmodel = '../3ds/vyper3R.3ds'
    logger.info('2 models are in %s' % testmodel)
    ''' test with a model that holds several objects '''
    models = parse3ds(testmodel)
    assert len(models) > 2
    m = models[1]
    #for m in models:
    name, V, F, T = m[0], m[1], m[2], m[3]
    logger.debug(name)
    logger.debug( 'V %s %s' % (type(V), type(V[0][2])))
    logger.debug( 'F %s %s' % (type(F), type(F[0][0])))
    logger.debug( 'T %s ' % (type(T) ))
