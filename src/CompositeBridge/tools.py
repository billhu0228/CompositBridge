from ezdxf.math import Vec3


class Recorder:
    def __init__(self, CG: "Vec3", ni: int, nj: int, res):
        self.ni = ni
        self.nj = nj
        self.cg = CG
        self.result = res


def read_res(filepath):
    with open(filepath) as fid:
        txt = fid.readlines()
        for i, line in enumerate(txt):
            if line.startswith(" BEAM188"):
                res=txt[i+3]
