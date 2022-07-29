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
            if line.startswith(" BEAM188   EL"):
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
                if len(res) != 7:
                    raise Exception(force_text)
                rec_dic = {"stage": cur_stage, "load_node": cur_node, 'e': ele,
                           'x': cg_vec.x, 'y': cg_vec.y, 'z': cg_vec.z, 'ni': ni, 'nj': nj,
                           'fx': res[0], 'my': res[1], 'mz': res[2], 'tq': res[3], 'sfz': res[4], 'sfy': res[5]}
                # rec = Recorder(cur_stage, secn, ele, cg_vec, ni, nj, res)
                data.append(rec_dic)
    ret = pd.DataFrame(data)
    return ret


def get_value(data, x0):
    if x0 in data[data.columns[0]].values:
        ret = data[data[data.columns[0]] == x0]
        return ret.values[-1][-1]
    else:
        data['abs'] = data[data.columns[0]].apply(lambda x: abs(x - x0))
        data.sort_values(['abs'], inplace=True)
        x1 = data.iloc[0][0]
        x2 = data.iloc[1][0]
        y1 = data.iloc[0][1]
        y2 = data.iloc[1][1]
        if x1 > x2:
            assert x1 > x0 > x2
        else:
            assert x2 > x0 > x1
        f1 = (x2 - x0) / (x2 - x1)
        f2 = (x0 - x1) / (x2 - x1)
        return f1 * y1 + f2 * y2


def get_envo(effect_matrix: pd.DataFrame, label: str, lane_factor, pk_factor, multi_factor, shear_factor):
    ret = effect_matrix[['x']].copy()
    ret[label + '_max'] = 0
    ret[label + '_min'] = 0
    for col in effect_matrix.columns:
        if col.startswith("my") or col.startswith('sfz'):
            ret[label + '_max'] += effect_matrix[col].where(effect_matrix[col] > 0, 0) * lane_factor * multi_factor
            ret[label + '_min'] += effect_matrix[col].where(effect_matrix[col] < 0, 0) * lane_factor * multi_factor
    force = effect_matrix.iloc[:, 5:].T
    aa = force.apply(lambda ser: ser.where(ser == ser.max(), 0)).T
    force_max = aa.apply(lambda row: row.sort_values(ascending=False, ignore_index=True), axis=1)[0]
    aa = force.apply(lambda ser: ser.where(ser == ser.min(), 0)).T
    force_min = aa.apply(lambda row: row.sort_values(ascending=True, ignore_index=True), axis=1)[0]
    ret[label + '_max'] += force_max * pk_factor * multi_factor * shear_factor
    ret[label + '_min'] += force_min * pk_factor * multi_factor * shear_factor
    return ret


def get_effect_matrix(res_data, lane_num, grider_loc, bridge):
    girder = res_data[(res_data.z == grider_loc) & (res_data.stage == 1)]
    girder = girder.drop(columns=['stage', 'load_node', 'fx', 'sfy', 'mz', 'tq', 'my', 'sfz'])
    girder.set_index(["e"], inplace=True)
    girder_my = girder.sort_values(by='x')
    girder_sfz = girder.sort_values(by='x')
    lane = [a for a in bridge.lane_matrix if a[0] == lane_num]
    lane_force_factor = bridge.length * 10500 / len(lane[0][-1]) / 1000.0
    peak_force_factor = bridge.live_load.Pk / 1000
    multi_ft = bridge.live_load.multi_factors
    for ii in range(len(lane[0][-1])):
        pts = [a[-1][ii] for a in lane]
        factors = [a[1] for a in lane]
        pt = pts[0]
        k = res_data[(res_data.load_node == pt) & (res_data.z == grider_loc)]
        k.set_index('e', inplace=True)
        my = k['my'] * 0
        sfz = k['sfz'] * 0
        for jj, fa in enumerate(factors):
            pt = pts[jj]
            k = res_data[(res_data.load_node == pt) & (res_data.z == grider_loc)]
            k.set_index('e', inplace=True)
            my += k['my'] * fa
            sfz += k['sfz'] * fa
        girder_my['my_%i' % ii] = my
        girder_sfz['sfz_%i' % ii] = sfz
    return girder_my, girder_sfz, (lane_force_factor, peak_force_factor, multi_ft)
