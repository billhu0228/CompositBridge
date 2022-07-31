from typing import Tuple


# from src.CompositeBridge import Node


class Element:
    __slots__ = ('e', 'nlist', 'mat', 'etype', 'real', 'secn', '_npts')

    nlist: Tuple["Node"]

    def __init__(self, e: int, mat: int, etype: int, real: int, secn: int, nodes: Tuple):
        self.e = e
        self.mat = mat
        self.etype = etype
        self.real = real
        self.secn = secn
        self._npts = len(nodes)
        if self.etype == 188:
            if len(nodes) != 3:
                raise Exception("BEAM188应使用3个Node.")
            else:
                self.nlist = nodes
        elif etype == 181 or etype == 182:
            if len(nodes) != 4:
                raise Exception("SHELL181应使用4个Node.")
            else:
                self.nlist = nodes
        elif etype == 1841 or etype == 1840:
            if len(nodes) != 2:
                raise Exception("MPC184应使用2个Node.")
            else:
                self.nlist = nodes
        else:
            raise Exception("单元类型不支持.")

    @property
    def apdl_str(self):
        cmd_str = '''mat,%i
type,%i
real,%i
secn,%i
e,''' % (self.mat, self.etype, self.real, self.secn)
        for nn in self.nlist:
            cmd_str += str(nn.n)
            cmd_str += ','
        return cmd_str

    def __str__(self):
        ss = "Elem: (%i,type=%i,secn=%i,nlist=[" % (self.e, self.etype, self.secn,)
        for n in self.nlist:
            ss += "%i," % n.n
        ss += "])"
        return ss
