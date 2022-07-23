import re

import pandas as pd
from ezdxf.math import Vec3


class Recorder:
    def __init__(self, stage: int, secn: int, e: int, CG: "Vec3", ni: int, nj: int, res):
        self.stage = stage
        self.e = e
        self.secn = secn
        self.ni = ni
        self.nj = nj
        self.cg = CG
        self.result = res

    def __str__(self):
        return "ST=%i,E=%i,CG=%s" % (self.stage, self.e, self.cg)


def text_to_dict(txt, load_no):
    res = re.split('\s+', txt)
    rec = {
        'load': load_no,
        'node': int(res[5]),
        'fx': float(res[6]),
        'fy': float(res[7]),
        'fz': float(res[8]),
        'mx': float(res[9]),
        'my': float(res[10]),
        'mz': float(res[11]),
    }
    return rec


def read_node_res(filepath):
    data = {}
    with open(filepath) as fid:
        txt = fid.readlines()
        text_idx_st = [txt.index(a) for a in txt if a.startswith("  LOAD STEP=")]
        text_idx_ed = [txt.index(a) for a in txt if a.startswith(" *** LOAD STEP")]
        for i in range(len(text_idx_ed)):
            st = text_idx_st[i]
            ed = text_idx_ed[i]
            cur_load = int(float(re.findall("(?<=TIME =).+(?= )", txt[st - 1])[0]))
            blk = txt[st + 1:ed]
            blk = [a for a in blk if a.startswith("  STATIC LOAD ON NODE")]
            blk = [text_to_dict(a, cur_load) for a in blk]
            out = pd.DataFrame(blk)
            out.sort_values(by='node', inplace=True, ignore_index=True)
            data[cur_load] = out
    return data


def read_res(filepath):
    data = []
    cur_stage = 0
    # secn = 0
    with open(filepath) as fid:
        txt = fid.readlines()
        for i, line in enumerate(txt):
            if line.startswith("  LOAD STEP= "):
                cur_stage = int(re.findall("(?<=STEP=).+(?=SUB)", line)[0])
                cur_node = int(float(re.findall("\d+\.\d+", txt[i - 1])[0]))
            if line.startswith(" BEAM188"):
                ele = int(re.findall("(?<=EL=).+(?=MAT)", line)[0])
                # secn = int(re.findall("(?<=SEC ID=).+(?=C\.G\.)", line)[0])
                cg_str = re.findall("(?<=C\.G\.=\().+  (?=\))", line)[0]
                cg_vec = Vec3([float(a) for a in cg_str.split(',')])
                nd_str: str = re.findall("(?<=NODES=).+", line)[0]
                nd_str = nd_str.strip()
                ni = int(nd_str.split(" ")[0])
                nj = int(nd_str.split(" ")[-1])
                force_text = txt[i + 3]
                pat = re.compile("-?\d+\.\d+E?-?\d?")
                res = re.findall(pat, force_text)
                res = [float(mm) for mm in res]
                if len(res) != 6:
                    raise Exception(force_text)
                rec_dic = {"stage": cur_stage, "load_node": cur_node, 'e': ele,
                           'x': cg_vec.x, 'y': cg_vec.y, 'z': cg_vec.z, 'ni': ni, 'nj': nj,
                           'fx': res[0], 'my': res[1], 'mz': res[2], 'tq': res[3], 'sfz': res[4], 'sfy': res[5]}
                # rec = Recorder(cur_stage, secn, ele, cg_vec, ni, nj, res)
                data.append(rec_dic)
    ret = pd.DataFrame(data)
    return ret
