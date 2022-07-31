from ezdxf.math import Vec3

from .base import ApdlWriteable


class Node(ApdlWriteable):
    __slots__ = ('n', 'x', 'y', 'z', '_location')

    def __init__(self, n: int, x, y, z):
        self._location = Vec3(x, y, z)
        self.n = n
        self.x = x
        self.y = y
        self.z = z

    @property
    def apdl_str(self):
        cmd_str = "n,%i,%.3f,%.3f,%.3f" % (self.n, self.x, self.z, self.y)
        return cmd_str

    def __str__(self):
        return "Node: (%i,%.3f,%.3f,%.3f)" % (self.n, self.x, self.y, self.z)

    def distance(self, other: 'Node'):
        return self._location.distance(other._location)

    def copy(self, dn: int = 0, x0: float = 0, y0: float = 0, z0: float = 0):
        return Node(self.n + dn, self.x + x0, self.y + y0, self.z + z0)

    def __eq__(self, other: 'Node'):
        return self.n == other.n

    def __ne__(self, other: 'Node'):
        return self.n != other.n

    def __gt__(self, other: 'Node'):
        return self.n > other.n

    def __lt__(self, other: 'Node'):
        return self.n < other.n

    def __ge__(self, other: 'Node'):
        return self.n >= other.n

    def __le__(self, other: 'Node'):
        return self.n <= other.n
