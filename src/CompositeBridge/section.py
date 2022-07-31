from abc import ABCMeta, abstractmethod
from typing import Tuple
from .base import ApdlWriteable


class Section:
    __slots__ = ('id', 'name', '_offset')
    __metaclass__ = ABCMeta

    def __init__(self, Id: int, Name: str, offset: Tuple[float, float]):
        self.id = Id
        self.name = Name
        self._offset = offset

    def __cmp__(self, other: "Section"):
        """compare two Section
        negative if self <  other;
        zero     if self == other;
        positive if self >  other;
        """
        return self.id - other.id

    def set_offset(self, x=0, y=0):
        self._offset = (x, y)

    @property
    def offset(self):
        return self._offset





class ShellSection(Section, ApdlWriteable):
    """
    Shell截面
    """

    __slots__ = ('thickness',)

    thickness: float

    def __init__(self, Id: int, Name: str, offset: Tuple[float, float], th: float):
        super().__init__(Id, Name, offset)
        self.thickness = th

    @property
    def apdl_str(self):
        cmd_str = ''' 
! Shell截面
sect,%i,shell,,%s
secdata, %.5f,1,0.0,3  
secoffset,user,%.5f  
seccontrol,,,, , , ,''' % (self.id, self.name, self.thickness, self._offset[1])
        return cmd_str

    def __str__(self):
        st = "%i : %s : (" % (self.id, self.name)
        for key in self.__slots__:
            st += "%.3f," % getattr(self, key)
        st += ")"
        return st


class ISection(Section, ApdlWriteable):
    """
    I型梁截面
    """

    __slots__ = ('w1', 'w2', 'w3', 't1', 't2', 't3')

    def __init__(self, Id: int, Name: str, offset: Tuple[float, float], **kwargs):
        super().__init__(Id, Name, offset)
        for key, value in kwargs.items():
            if key in self.__slots__:
                setattr(self, key, value)

    def __str__(self):
        st = "%i : %s : (" % (self.id, self.name)
        for key in self.__slots__:
            st += "%.3f," % getattr(self, key)
        st += ")"
        return st

    @property
    def apdl_str(self):
        cmd_str = '''
! I型梁截面
sect,  %i, BEAM, I, %s, 0   
secoffset, user, %f, %f 
secdata,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,0,0,0,0,0,0''' % (
            self.id, self.name, self._offset[0], self._offset[1],
            self.w1, self.w2, self.w3, self.t1, self.t2, self.t3)
        return cmd_str

    @property
    def yg(self):
        h = self.w3 - self.t1 - self.t2
        a1 = self.t1 * self.w1
        a3 = self.t3 * h
        a2 = self.t2 * self.w2
        y1 = 0.5 * self.t1
        y3 = self.t1 + 0.5 * h
        y2 = self.w3 - self.t2 * 0.5
        y0 = (y1 * a1 + y2 * a2 + y3 * a3) / self.area
        return y0

    @property
    def area(self):
        return self.w1 * self.t1 + self.w2 * self.t2 + (self.w3 - self.t1 - self.t2) * self.t3

    @property
    def inertia(self):
        h = self.w3 - self.t1 - self.t2
        a1 = self.t1 * self.w1
        a3 = self.t3 * h
        a2 = self.t2 * self.w2
        y1 = 0.5 * self.t1
        y3 = self.t1 + 0.5 * h
        y2 = self.w3 - self.t2 * 0.5
        y0 = (y1 * a1 + y2 * a2 + y3 * a3) / self.area
        i1 = self.t1 ** 3 * self.w1 / 12 + a1 * (y0 - y1) ** 2
        i2 = self.t2 ** 3 * self.w2 / 12 + a2 * (y0 - y2) ** 2
        i3 = self.t3 * h ** 3 / 12 + a3 * (y0 - y3) ** 2
        i = i1 + i2 + i3
        return i


class Material(ApdlWriteable):
    __slots__ = ('id', 'ex', 'dens', 'alpx', 'nuxy', 'description')

    def __init__(self, id, ex, dens, alpx, nuxy, description: str = ''):
        self.id = id
        self.ex = ex
        self.dens = dens
        self.alpx = alpx
        self.nuxy = nuxy
        self.description = description

    @property
    def apdl_str(self):
        cmd_str = '''
!%s
MP,EX,  %i,%.4e
MP,DENS,%i,%.4e
MP,ALPX,%i,%.4e
MP,NUXY,%i,%.1f''' % (self.description,
                      self.id, self.ex,
                      self.id, self.dens,
                      self.id, self.alpx,
                      self.id, self.nuxy
                      )
        return cmd_str


if __name__ == "__main__":
    t1 = ISection(1, "I300", w1=1, w2=1, w3=1, t1=1, t2=1, t3=1)
    t2 = Material(1, 206000, 7.85e-9, 1.2e5, 0.3, 'Q420')
    print(t2.apdl_str)
