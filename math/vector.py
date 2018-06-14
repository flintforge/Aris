'''
    A vector helper
    License: AGPLv3, see LICENSE for more details
    Copyright: 2011 Florian Boesch <pyalot@gmail.com>
'''

class Vec2:
    def __init__(_, x=0, y=0):
        _.x = float(x)
        _.y = float(y)

    def __sub__(_, other):
        return Vec2(
            _.x - other.x,
            _.y - other.y,
        )

    def __iter__(_):
        return iter((_.x, _.y))


class Vec3:
    def __init__(_, x=0, y=0, z=0):
        _.x = float(x)
        _.y = float(y)
        _.z = float(z)

    def cross(s, o):
        return Vec3(
            s.y*o.z - o.y*s.z,
            s.z*o.x - o.z*s.x,
            s.x*o.y - o.x*s.y,
        )

    def dot(s, o):
        return s.x*o.x + s.y*o.y + s.z*o.z

    def __sub__(_, other):
        return Vec3(
            _.x - other.x,
            _.y - other.y,
            _.z - other.z,
        )

    def __add__(_, other):
        return Vec3(
            _.x + other.x,
            _.y + other.y,
            _.z + other.z,
        )

    def __iadd__(_, other):
        _.x += other.x
        _.y += other.y
        _.z += other.z
        return _

    def __mul__(_, scalar):
        return Vec3(
            _.x * scalar,
            _.y * scalar,
            _.z * scalar,
        )

    def __div__(_, scalar):
        return Vec3(
            _.x / scalar,
            _.y / scalar,
            _.z / scalar,
        )

    def __idiv__(_, scalar):
        _.x /= scalar
        _.y /= scalar
        _.z /= scalar
        return _

    def normalize(_):
        length = (_.x*_.x + _.y*_.y + _.z*_.z)**0.5
        return Vec3(
            _.x/length,
            _.y/length,
            _.z/length,
        )

    def __iter__(_):
        return iter((_.x, _.y, _.z))
