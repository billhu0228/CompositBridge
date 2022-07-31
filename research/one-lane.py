import json
import pickle
import numpy as np
import pandas as pd
from src.CompositeBridge import *
from src.CompositeBridge.load import GBLiveLoad
from src.CompositeBridge.tools import read_res, get_effect_matrix, get_envo, get_value
from src.mechanics import calculate


def run(file, span_length, nspan, g_spacing, g_h, Nb, c_spacing, c_h, ts, ):
    name = "%i-%.0fm-%.1f-%i-%i" % (nspan, span_length, g_spacing, Nb, ts * 1000)
    g1 = [1.2] + [g_spacing, ] * (Nb - 1) + [1.2]
    g2 = [sum(g1), ]
    ca = CrossArrangement(sum(g1), g1, g2, ts, 0.05, 0.3, 0.0)
    sps = []
    for i in range(nspan + 1):
        s = Span(span_length * i)
        sps.append(s)
    m1 = Material(1, 206000e6, 7850, 1.2e5, 0.3, 'Q420')
    m2 = Material(2, 206000e6, 7850, 1.2e5, 0.3, 'Q345')
    m3 = Material(3, 34500e6, 2500, 1.1e5, 0.2, 'Concrete')
    m184 = Material(184, 0, 0, 0, 0, 'MP184')
    Bridge = CompositeBridge(sps, ca, cross_beam_dist=c_spacing)
    Bridge.add_material(m1)
    Bridge.add_material(m2)
    Bridge.add_material(m3)
    Bridge.add_material(m184)
    s1 = ShellSection(1, 'Slab', th=ts, offset=(0, ts * 0.5 + 0.05))
    s2 = ISection(2, "MainGd", offset=(0, g_h), w1=0.7, w2=0.6, w3=g_h, t1=0.032, t2=0.024, t3=0.018)
    s3 = ISection(3, "I300", offset=(0, 0.3), w1=0.3, w2=0.6, w3=0.3, t1=0.010, t2=0.010, t3=0.008)
    s4 = ISection(4, "I700", offset=(0, c_h), w1=0.3, w2=0.3, w3=0.7, t1=0.024, t2=0.024, t3=0.013)
    s5 = ISection(5, "I300", offset=(0, 0.3), w1=0.3, w2=0.3, w3=0.3, t1=0.010, t2=0.010, t3=0.008)
    Bridge.add_section(s1)
    Bridge.add_section(s2)
    Bridge.add_section(s3)
    Bridge.add_section(s4)
    Bridge.add_section(s5)
    Bridge.generate_fem(2, 0.5, 181)
    modelName = name
    LiveLoad = GBLiveLoad(Bridge.cal_span, loc=[1.2 + g_spacing])
    Bridge.add_live_load(LiveLoad)  # 定义车道位置，国标
    Bridge.write_database(path=r"E:\20220217 组合梁论文\02 Python\bin\%s" % modelName, projectname="TestModelA")
    Bridge.run_ansys(path=r"E:\20220217 组合梁论文\02 Python\bin\%s" % modelName)
    filepath = "../bin/%s/liveload.res" % modelName
    rr = read_res(filepath)
    girderZ = 1.2 + g_spacing
    my_x, sfz_x, fts = get_effect_matrix(rr, lane_num=0, grider_loc=girderZ, bridge=Bridge)
    lane1_my = get_envo(my_x, 'my', fts[0], fts[1], fts[2], 1.0)
    My1 = get_value(lane1_my[['x', 'my_min']], 0.5 * span_length)
    LL = [span_length, ] * nspan  # , 40, 40, 40]
    xs = [a for a in range(sum(LL) + 1)]
    res = {'x': xs}
    for x in xs:
        r = calculate(LL, cForce=[x], moment_loc=xs, shear_loc=xs)
        res['my_%i' % x] = r['m']
    res = pd.DataFrame(res)
    kk = get_envo(res, 'my', 10500, LiveLoad.Pk, 1, 1.0)
    My2 = get_value(kk[['x', 'my_min']], 0.5 * span_length)
    result = {
        "nspan": nspan,
        "S": g_spacing,
        "L": span_length,
        "ts": ts,
        "Kg": Bridge.get_parameters()['Kg'],
        "Sc": c_spacing,
        "Nb": Nb,
        "Hg": g_h,
        "Hc": c_h,
        "g": My1 / My2
    }
    with open(file, 'a') as fid:
        fid.write(json.dumps(result) + '\n')
    return {"Name": modelName, "F3d": My1, "Fbeam": My2, "g": My1 / My2}


if __name__ == "__main__":
    file = "one-lane-result.dat"
    for ch in [0.3, 0.5,]:
        res = run(file, span_length=40, nspan=1, g_spacing=4.0, g_h=1.8, Nb=5, c_spacing=5, c_h=ch, ts=0.25, )
        print(res)
