'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:43>
Released under the MIT License

todo : if needed, compile from a string instead of a file
'''

import re
from OpenGL.GL import *
import logging as logger
from ansicolor import AnsiColors as Ansi
from collections import OrderedDict


class ShaderCompiler():

    @classmethod
    def compile(Cls, vsfile=None, fsfile=None):

        with open(vsfile, 'r') as vsf:
            with open(fsfile, 'r') as fsf:
                vs_src, fs_src = (vsf.read(), fsf.read())

                program = glCreateProgram()

                if vs_src:  # yeah-yeah you can try if you want without one or the other
                    vertex_shader = Cls.create_shader(
                        GL_VERTEX_SHADER, vs_src, vsfile)
                    glAttachShader(program, vertex_shader)

                if fs_src:
                    fragment_shader = Cls.create_shader(
                        GL_FRAGMENT_SHADER, fs_src, fsfile)
                    glAttachShader(program, fragment_shader)

                glLinkProgram(program)
                message = Cls.get_program_log(program)
                if message:
                    logger.debug(
                        'Shader: shader program message: %s' % message)

                variables = Cls.get_variables('%s\n%s' % (vs_src, fs_src))

                return (program, variables)

    @classmethod
    def create_shader(self, shader_type, source, file):
        shader = glCreateShader(shader_type)
        # PyOpenGL bug ? He's waiting for a list of string, not a string
        # on some card, failure occured. keep an eye on it.
        if isinstance(source, str):
            source = [source]
        glShaderSource(shader, source)
        glCompileShader(shader)
        message = self.get_shader_log(shader)
        if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
            logger.error('%s %s' % (file,glGetShaderInfoLog(shader).decode()))
            raise RuntimeError( Ansi.RED + file + Ansi.YELLOW + Ansi.OFF )
        if message:
            logger.debug('Shader: message: %s' % message)
        return shader

    @classmethod
    def get_shader_log(cls, shader):
        '''Return the shader log'''
        return cls.get_log(shader, glGetShaderInfoLog)

    @classmethod
    def get_program_log(cls, shader):
        '''Return the program log'''
        return cls.get_log(shader, glGetProgramInfoLog)

    @classmethod
    def get_log(cls, obj, func):
        value = func(obj)
        return value

    @classmethod
    def get_variables(cls, src):
        """ return (attrib,locations, and uniforms)
            A glUniform template is in  use to determine automatically the type.
        """
        # Get one string of code with comments removed
        code = re.sub(r'(.*)(//.*)', r'\1', src, re.M)
        # Regexp to look for variable names
        var_regexp = ("\s*VARIABLE\s+"  # kind of variable
                      "((highp|mediump|lowp)\s+)?"  # Precision (optional)
                      "(?P<type>\w+)\s+"  # type
                      "(?P<name>\w+)\s*"  # name
                      "(\[(?P<size>\d+)\])?"  # size (optional)
                      "(\s*\=\s*[0-9.]+)?"  # default value (optional)
                      "\s*;"  # end
                      )

        # Parse uniforms, attributes and varyings
        _variables = OrderedDict()
        for kind in ('uniform', 'attribute', 'varying', 'const'):
            regex = re.compile(var_regexp.replace('VARIABLE', kind),
                               flags=re.MULTILINE)
            for m in re.finditer(regex, code):
                gtype = m.group('type')
                size = int(m.group('size')) if m.group('size') else -1
                this_kind = kind
                if size >= 1:
                    # uniform arrays get added both as individuals and full
                    for i in range(size):
                        name = '%s[%d]' % (m.group('name'), i)
                        _variables[name] = kind, gtype, name, -1
                    this_kind = 'uniform_array'
                name = m.group('name')
                _variables[name] = this_kind, gtype, name, size
        return _variables


# tests ##################################################################

def testShaderParser():
    with open('../shaders/MVPTCL1.vs', 'r') as vsf:
        with open('../shaders/T3AL1.fs', 'r') as fsf:
            vs_src, fs_src = (vsf.read(), fsf.read())
    print(ShaderCompiler.get_variables(vs_src))
    print(ShaderCompiler.get_variables(fs_src))


if __name__ == '__main__':
    testShaderParser()
    # todo : create a quick gl context and compile please
