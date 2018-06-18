'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:50>
Released under the MIT License
'''
import os
from texture import Texture1D, Texture2D, Texture3D, Tex as Texture
from model import Model, Import3ds
from parse3ds import *
from shader import Shader
from pyglet import image
from pyglet.image import ImageData
from seagull.xml import parse
from seagull.scenegraph.element import Use as SvgGroup
import seagull.scenegraph as Sg

# from svgutils import printSvgIds

import logging
logger = logging.getLogger('log.%s' % __name__)
'''
How it works :

declare resources attached to a file, like :

    resources = {
        'tex1': 'uv.png',
        'models': ['spacship','skydome','monkey','3ds'],
        'shader' : ['vertex.vs','fragment.fs','glsl']
    }
    Resource.load(resources,obj)

the keys of the dictionnary get automatically bound as members to the object
(obj.tex1, obj.models, etc)

add a file watcher able to provide at runtime any file modified, and
reverse lookup the key from the dict :

slot = reverseLookDict(resources, file)
Resource.TypedFactory(obj.__dict__[slot],file)

The attribute will be automagically updated/rebuilded when the file gets modified.
ace.

'''


DEFAULT_RESOURCE_LOC = 'GFX'
ResourceLocation = {
    'Tex' : 'GFX',
    'Texture2D': 'GFX',
    'Texture3D': './images/',
    'Model3ds': '../3ds/',
    'Model': '../3ds/',
    'GLSLShader': './shaders/',
    'Shader': './shaders/',
    'Image': './GFX/',
    'ImageData': './GFX/',
    'Svg' : './',
    'Use' : './' # svg

}
# needs class by name to go further
# get_class = lambda x: globals()[x]
# If you need to get a class from a module, you can use getattr:
# import urllib2
# handlerClass = getattr(urllib2, 'HTTPHandler')


def openfile(filepath):
    #path, filename = os.path.split(filename)
    if filepath.endswith('z'):
        f = gzip.open(filepath,'rt')
    else:
        f = open(filepath)
    r = f.read()
    f.close()
    return r

def Model3ds(file):
    return Import3ds(*parse3ds(file))

def GLSLShader(vs, fs):
    return Shader(vs, fs)

def Image(file):
    return image.load(os.path.join(file))

def Svg(file):
    svgFile = parse(openfile(file))
    # printSvgIds(svgFile)
    svg = SvgGroup(svgFile)
    setattr(svg,'updated',False)
    return svg

def Tex(file):
    return Texture(file)


class Resource:

    def Factory(member, attribute):

        if type(attribute) is not list:
            raise Exception(
                'Factory except a list as member. %s provided' % type(attribute))

        klass = attribute[0]
        loc = ResourceLocation.get(klass.__name__, DEFAULT_RESOURCE_LOC)
        files = attribute[1]
        logger.debug('%s %s %s ' % (klass,loc,files))
        if type(files) is list:
            member = [klass(os.path.join(loc,f)) for f in files]
        elif type(files) is tuple:
            member = klass(*(os.path.join(loc,f) for f in files))
        else:
            member = klass(os.path.join(loc,files))

        return member

    def load(resource, obj):
        for (member, attribute) in resource.items():
            obj.__dict__[member] = Resource.Factory(member, attribute)  # globals()[slot](file)

    def reload(file, slot):
        ''' update time.
            don't reassign the slot or the holding object won't see it
        '''
        loc = ResourceLocation[type(slot).__name__]
        logger.debug('reload %s %s' % (file, type(slot)))

        if type(slot) is Texture:  # refine its type
            # res = Resource.Factory(file) # instanciate the raw material
            slot.load(os.path.join(loc,file))  # = tex.create(image)

        elif type(slot) is SvgGroup:
            # res = Resource.Factory(file) # we need a fromFile method in our
            # texture
            slot.__init__(parse(openfile(os.path.join(loc,file))))
            slot.updated = True

        elif type(slot) is Texture2D:  # refine its type
            # res = Resource.Factory(file) # instanciate the raw material
            slot.fromFile(os.path.join(loc,file))  # = tex.create(image)
        elif type(slot) is Texture3D:
            # res = Resource.Factory(file) # we need a fromFile method in our
            # texture
            slot.fromFile(file)
        elif type(slot) is ImageData:
            # res = Resource.Factory(file) # we need a fromFile method in our
            # texture
            img = image.load( os.path.join(loc,file))
            slot.set_data(img.format, img.pitch, img.data)

        elif type(slot) is Shader:
            ext = file[len(file) - 3:]
            if ext == '.vs':
                slot.compileVS(loc + file)
            elif ext == '.fs':
                slot.compileFS(loc + file)
            else:
                raise Exception('Dont know how to build', ext)

        elif type(slot) is Model:
            slot = Model3ds(file) # wrong

        else:
            logger.error('Typed Factory dont know how to assemble %s with %s' % (type(slot), file))
            #raise Exception('Typed Factory dont know how to assemble', type(slot), 'with', file)


if __name__ == '__main__':

    from dictmixins import DictMixins

    class objdefined(object):
        """ base object has no dict,
        so we can just write obj=object()
        and end writing one here """

        def __init__(self):
            res = {'tex1': 'uv.png',
                   'tex2': '3dtac256.png',
                   'tex3': '3dtactic.png',
                   'models': ['tetrahedron', 'cube', 'uvsphere', 'icosphere', 'monkey', '3ds']}

            self.res = {
                'tex1': [Texture3D, 'uv.png'],
                'tex2': [Texture2D, '3dtac256.png'],
                'img1': [Image, '3dtactic.png'],
                'models': [Model3ds, ['tetrahedron.3ds', 'cube.3ds', 'uvsphere.3ds', 'icosphere.3ds', 'monkey.3ds']],
                'MVPTCL1_T3AL1': [GLSLShader, ('MVPTCL1.vs', 'T3AL1.fs')],
                'PostProcess': [GLSLShader, ('pp.vs', 'pp.fs')]
            }
            DictMixins.__init__(self, res)
            Resource.load(self.res, self)
            pass

    obj = objdefined()
    Resource.reload('./images/uv.png', obj.tex1)
    Resource.reload('./3ds/tetrahedron.3ds', obj.models[0])
    Resource.reload('./images/3dtactic.png', obj.img1)
    ''' todo : keep testing with a filewatcher, twice '''
