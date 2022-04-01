import re

import pandas as pd
from ezdxf.math import Vec3


class Recorder:
    def __init__(self, stage: int, e: int, CG: "Vec3", ni: int, nj: int, res):
        self.stage = stage
        self.e = e
        self.ni = ni
        self.nj = nj
        self.cg = CG
        self.result = res


def read_res(filepath):
    out = pd.DataFrame([], columns=['stage', 'e', 'ni', 'nj', 'cg', 'result'])
    data=[]
    cur_stage = 0
    with open(filepath) as fid:
        txt = fid.readlines()
        for i, line in enumerate(txt):
            if line.startswith("  LOAD STEP= "):
                cur_stage = int(re.findall("(?<=STEP=).+(?=SUB)", line)[0])
            if line.startswith(" BEAM188"):
                ele = int(re.findall("(?<=EL=).+(?=MAT)", line)[0])
                cg_str = re.findall("(?<=C\.G\.=\().+  (?=\))", line)[0]
                cg_vec = Vec3([float(a) for a in cg_str.split(',')])
                nd_str: str = re.findall("(?<=NODES=).+", line)[0]
                nd_str = nd_str.strip()
                ni = int(nd_str.split(" ")[0])
                nj = int(nd_str.split(" ")[-1])
                force_text = txt[i + 3]
                pat = re.compile("-?0\.\d+E-?\d+")
                res = re.findall(pat, force_text)
                res = [float(mm) for mm in res]
                rec = Recorder(cur_stage, ele, cg_vec, ni, nj, res)
                data.append(rec)
    return data
