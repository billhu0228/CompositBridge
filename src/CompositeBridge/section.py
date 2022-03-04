from abc import ABCMeta, abstractmethod


class ApdlWriteable:
    __metaclass__ = ABCMeta

    @abstractmethod
    def apdl_str(self):
        pass


class Section:
    __slots__ = ('id', 'name', '_offset')
    __metaclass__ = ABCMeta

    def __init__(self, Id: int, Name: str, **kwargs):
        self.id = Id
        self.name = Name
        self._offset = (0, 0)

    def __cmp__(self, other: "Section"):
        """compare two Section
        negative if self <  other;
        zero     if self == other;
        positive if self >  other;
        """
        return self.id - other.id

    def set_offset(self, x=0, y=0):
        self._offset = (x, y)


class ISection(Section, ApdlWriteable):
    """
    I型梁截面
    """

    __slots__ = ('w1', 'w2', 'w3', 't1', 't2', 't3')

    def __init__(self, Id: int, Name: str, **kwargs):
        super().__init__(Id, Name)
        for key, value in kwargs.items():
            if key in self.__slots__:
                setattr(self, key, value)

    def __str__(self):
        st = "%i : %s : (" % (self.id, self.name)
        for key in self.__slots__:
            st += "%.1f," % getattr(self, key)
        st += ")"
        return st

    @property
    def apdl_str(self):
        cmd_str = '''
SECTYPE,  %i, BEAM, I, %s, 0   
SECOFFSET, USER, %f, %f 
SECDATA,%.3f,%.3f,%.3f,%.3f,%.3f,%.3f,0,0,0,0,0,0''' % (
            self.id, self.name, self._offset[0], self._offset[1],
            self.w1, self.w2, self.w3, self.t1, self.t2, self.t3)
        return cmd_str


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
