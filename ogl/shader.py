'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:43>
Released under the MIT License
'''
from OpenGL.GL import *
from shadercompiler import ShaderCompiler
from ctypes import sizeof, c_float, c_void_p, c_uint
import debuglog
log = debuglog.init(__name__)

# goes in the c_size package
uint_size = sizeof(c_uint)
float_size = sizeof(c_float)

""" Important :
the order of attributes in the shader source matters.
The attributes MUST be declared in the same
order as the VBO packing occured :
index are automatically bound to location

exemple :
vertex_offset    = c_void_p(0 * float_size)
tex_coord_offset = c_void_p(3 * float_size)
normal_offset    = c_void_p(6 * float_size)
color_offset     = c_void_p(9 * float_size)
"""
record_len = 12 * float_size

# used for attributes locations
var_size = {
    'vec2': (2, float_size),
    'vec3': (3, float_size),
    'mat3': (9, float_size),
    'mat4': (16, float_size)
}


def typesize(type):
    var = var_size[type]
    return var[0] * var[1]


class Shader():
    """ Holds attribute, autobound at initialization and activation
        the order of declaration of the variables in the shader *matters*
        They should stick to the same order as the buffer data
        the general rule of thumb is V,T,N,C
    """

    Func = {
        'bool': glUniform1i,
        'int': glUniform1i,
        'float': glUniform1f,
        'sampler2D': glUniform1i,
        'sampler3D': glUniform1i,
        'samplerCube': glUniform1i,
        'vec2': glUniform2f,
        'ivec2': glUniform2i,
        'vec3': glUniform3f,
        'mat4': glUniformMatrix4fv
    }

    def __init__(self, vsfile, fsfile):

        self.vsfile = vsfile
        self.fsfile = fsfile
        self.compile()

    def compile(self):
        try:
            self.program, variables = ShaderCompiler.compile(
                self.vsfile, self.fsfile)
        except Exception as e:
            # need a default red shader
            log.error(e)
            return None

        ''' bind uniforms and attributes '''
        self.uniforms = dict((k,
                              (Shader.Func[v[1]],
                               glGetUniformLocation(self.program, k))
                              )
                             for (k, v) in variables.items() if v[0] == 'uniform')

        self.attribs = [
            (k, v)
            for (k, v) in variables.items() if v[0] == 'attribute']
        self.loc_attrib = {}
        self.stride = 0

        offset = 0
        log.info('compiling ' + self.vsfile + self.fsfile)
        for (i, (k, var)) in enumerate(self.attribs):
            # var hold (uniform|attribute,type,name,valueset (-1))
            log.debug('%i %s %s' % (i, k, var))
            size = var_size[var[1]]

            glBindAttribLocation(self.program, i, k)
            # var => ( i=location, 2|3, offset)
            self.loc_attrib[k] = (i, size[1], c_void_p(offset))  # loc[ ]
            offset += size[0] * size[1]  # 3*float_size

        self.stride = offset

        self.enableAttributes()

    ''' update file and recompile '''

    def compileVS(self, vsfile):
        self.vsfile = vsfile
        self.compile()

    def compileFS(self, fsfile):
        self.fsfile = fsfile
        self.compile()

    def use(self):
        glUseProgram(self.program)

    def __enter__(self):
        '''Use the shader'''
        glUseProgram(self.program)

    """ to reconsider when we just switch program. test it now"""

    def __exit__(self, exc_type, exc_value, traceback):
        '''Stop using the shader'''
        glUseProgram(0)

    def __setitem__(self, var, value):
        """ the called function might accept multiple arguments
            thus they need to be passed as arrays
            program['afloat'] = [f]
            program['avec2'] = [x,y]
            program['amat4'] = [1,Cmajor,mat]
        """
        item = self.uniforms[var]
        item[0](item[1], *value)

    def enableAttributes(self):
        """ enable vertex arrays
            this can comes at a cost to flexibilty,
            but we could always give the list of attributes
            to exclusively activate
        """
        for attrib, var in self.attribs:
            glEnableVertexAttribArray(self.loc_attrib[attrib][0])

    def activateAttributes(self):
        # assume only 32bits float for now...
        for (attrib, loc) in self.loc_attrib.items():
            glVertexAttribPointer(
                loc[0], loc[1], GL_FLOAT, False, self.stride, loc[2])
