'''
ARIS
Author:  𝓟𝓱𝓲𝓵.𝓔𝓼𝓽𝓲𝓿𝓪𝓵  @ 𝓕𝓻𝓮𝓮.𝓯𝓻
Date:<2018-05-18 15:52:43>
Released under the MIT License
'''
from OpenGL.GL import *
from model import Mesh,Model
from math import pi as PI, sin, cos
from random import randrange
#from linalg import matrix as _m

def axisArrow(L=1):

    glDisable(GL_TEXTURE_2D)
    glBegin(GL_LINE_STRIP)

    glColor3f(1, 0, 0)
    glVertex3f(L, 0, 0)
    glColor3f(1, 1, 1)
    glVertex3f(0, 0, 0 )
    glColor3f(0, 1, 0)
    glVertex3f(0, L, 0)
    glEnd()

    glBegin(GL_LINES)
    glColor3f(0, 0, 1)
    glVertex3f(0, 0, L )
    glColor3f(1, 1, 1)
    glVertex3f(0, 0, L)
    glEnd()
    glEnable(GL_TEXTURE_2D)



def QuadTex2(w=1,h=1,withtex=True, withnormals=True):
    # +texcorrds
    vertices = [[-w, -h, 0],
                [ w, -h, 0],
                [ w,  h, 0],
                [-w,  h, 0]]
    texcoords = [[0, 0],
                 [1, 0],
                 [1, 1],
                 [0, 1]]

    faces = [0, 1, 2, 2, 0, 3]
    normals = vertices if withnormals else None
    colors = vertices if withtex else None
    # find out how to discard extra data from the hstack
    mesh = Mesh(vertices, faces, normals, colors)
    model = Model(mesh, texcoords if withtex else None)
    return model



def quad(w=1,h=1,x=0,y=0,z=0,r=0):
    quad = [[-w+x, -h+y, z],
            [ w+x, -h+y, z],
            [ w+x,  h+y, z],
            [-w+x,  h+y, z]]
    return [
        [
            (X * cos(r) - Y * sin(r)),
            (X * sin(r) + Y * cos(r)),
            z
        ] for (X,Y,Z) in quad
    ]


def Quad2D(
    vertices=[[-1, -1, 0],
              [ 1, -1, 0],
              [ 1,  1, 0],
              [-1,  1, 0]],
    texcoords=[[0, 0],
               [1, 0],
               [1, 1],
               [0, 1]]) :

    faces = [0, 1, 2, 2, 3, 0]
    # find out how to discard extra data from the hstack
    mesh = Mesh(vertices,faces)
    model = Model(mesh, texcoords)
    return model


def Quad(x,y,w,h) :
    vertices = [[x,   y,   0],
                [x+w, y,   0],
                [x+w, y+h, 0],
                [w,   y+h, 0]],

    texcoords = [[0, 0],[1, 0], [1, 1], [0, 1]]

    faces = [0, 1, 2, 2, 3, 0]
    # find out how to discard extra data from the hstack
    # I ndexedbuffer.py", line 23, in __init__ : data = hstack(args).flatten()
    mesh = Mesh(vertices,faces)
    model = Model(mesh, texcoords)
    return model



def drawQuad00(tex,w,h):
        glBindTexture(GL_TEXTURE_2D,  tex)
        glBegin(GL_QUADS)
        glTexCoord2i(0, 1) ; glVertex2f(0, 0)
        glTexCoord2i(1, 1) ; glVertex2f(w, 0)
        glTexCoord2i(1, 0) ; glVertex2f(w, h)
        glTexCoord2i(0, 0) ; glVertex2f(0, h)
        glEnd()


def CloudQuads(W=(1,1),n=3, rnd=(10,10), withtex=True, withnormals=True):
    ''' a random field of n quads
        of random sizes in W,
        positionned over (x,y) in rnd
        of increasing z position of 1 by cloud
    '''
    vertices = []
    faces = []
    texcoords = []
    seq = [0, 1, 2, 2, 3, 0]
    texquad = [[0, 0],
               [1, 0],
               [1, 1],
               [0, 1]]

    for i in range(n):
        s = randrange(*W)
        x,y,z = randrange(-rnd[0],rnd[0]),randrange(-rnd[1],rnd[1]),i
        vertices += quad(s,s,x,y,z, randrange(180))
        faces += seq
        texcoords += texquad
        seq = [i+4 for i in seq]

    normals = vertices if withnormals else None
    colors = vertices if withtex else None

    mesh = Mesh(vertices, faces, normals, colors)
    model = Model(mesh, texcoords if withtex else None)
    return model







'''
def icosahedron() :
    X = .525731112119133606;
    Z = .850650808352039932;
    N = 0
    vertices = [
        (-X,N,Z), (X,N,Z), (-X,N,-Z), (X,N,-Z),
        (N,Z,X), (N,Z,-X), (N,-Z,X), (N,-Z,-X),
        (Z,X,N), (-Z,X, N), (Z,-X,N), (-Z,-X, N)
    ]

    triangles = [
        (0,4,1),(0,9,4),(9,5,4),(4,5,8),(4,8,1),
        (8,10,1),(8,3,10),(5,3,8),(5,2,3),(2,7,3),
        (7,10,3),(7,6,10),(7,11,6),(11,0,6),(0,1,6),
        (6,1,10),(9,0,11),(9,11,2),(9,2,5),(7,2,11)
    ]

'''

'''

using Lookup=std::map<std::pair<Index, Index>, Index>;

Index vertex_for_edge(Lookup& lookup,
  VertexList& vertices, Index first, Index second)
(
  Lookup::key_type key(first, second);
  if (key.first>key.second)
    std::swap(key.first, key.second);

  auto inserted=lookup.insert((key, vertices.size()});
  if (inserted.second)
  (
    auto& edge0=vertices[first];
    auto& edge1=vertices[second];
    auto point=normalize(edge0+edge1);
    vertices.push_back(point);
  }

  return inserted.first->second;
}


struct Triangle
(
  Index vertex[3];
};

using TriangleList=std::vector<Triangle>;
using VertexList=std::vector<v3>;

namespace icosahedron
(
const float X=.525731112119133606f;
const float Z=.850650808352039932f;
const float N=0.f;

static const VertexList vertices=
(
  (-X,N,Z}, (X,N,Z}, (-X,N,-Z}, (X,N,-Z},
  (N,Z,X}, (N,Z,-X}, (N,-Z,X}, (N,-Z,-X},
  (Z,X,N}, (-Z,X, N}, (Z,-X,N}, (-Z,-X, N}
};

static const TriangleList triangles=
(
  (0,4,1},(0,9,4},(9,5,4},(4,5,8},(4,8,1},
  (8,10,1},(8,3,10},(5,3,8},(5,2,3},(2,7,3},
  (7,10,3},(7,6,10},(7,11,6},(11,0,6},(0,1,6},
  (6,1,10},(9,0,11},(9,11,2},(9,2,5},(7,2,11}
};
}


using Lookup=std::map<std::pair<Index, Index>, Index>;

Index vertex_for_edge(Lookup& lookup,
  VertexList& vertices, Index first, Index second)
(
  Lookup::key_type key(first, second);
  if (key.first>key.second)
    std::swap(key.first, key.second);

  auto inserted=lookup.insert((key, vertices.size()});
  if (inserted.second)
  (
    auto& edge0=vertices[first];
    auto& edge1=vertices[second];
    auto point=normalize(edge0+edge1);
    vertices.push_back(point);
  }

  return inserted.first->second;
}


TriangleList subdivide(VertexList& vertices,
  TriangleList triangles)
(
  Lookup lookup;
  TriangleList result;

  for (auto&& each:triangles)
  (
    std::array<Index, 3> mid;
    for (int edge=0; edge<3; ++edge)
    (
      mid[edge]=vertex_for_edge(lookup, vertices,
        each.vertex[edge], each.vertex[(edge+1)%3]);
    }

    result.push_back((each.vertex[0], mid[0], mid[2]});
    result.push_back((each.vertex[1], mid[1], mid[0]});
    result.push_back((each.vertex[2], mid[2], mid[1]});
    result.push_back((mid[0], mid[1], mid[2]});
  }

  return result;
}

using IndexedMesh=std::pair<VertexList, TriangleList>;

IndexedMesh make_icosphere(int subdivisions)
(
  VertexList vertices=icosahedron::vertices;
  TriangleList triangles=icosahedron::triangles;

  for (int i=0; i<subdivisions; ++i)
  (
    triangles=subdivide(vertices, triangles);
  }

  return(vertices, triangles};
}


"""
icosphere mapping
const float kOneOverPi = 1.0 / 3.14159265;
float u = 0.5 - 0.5 * atan( N.x, -N.z ) * kOneOverPi;
float v = 1.0 - acos( N.y ) * kOneOverPi;
"""

'''
