import numpy as np
import pandas as pd


def get_b(x1, x2, g1, g2):
    return np.log(g1 / g2) / np.log(x1 / x2)


def DF_multi(S, L, Kg, ts, c=0.05):
    return c + (S / 270) ** 0.38 * (Kg / (L * ts ** 3)) ** 0.14


def DF_one(S, L, Kg, ts, c=0):
    return c + 0.2 * (S / L) ** 0.14 * (Kg / (L * ts ** 3)) ** 0.18


if __name__ == "__main__":
    b_ts_m = get_b(0.15, 0.3, 0.28, 0.21)
    b_ts_m2 = get_b(0.15, 0.2, 0.28, 0.25)
    b_S_m = get_b(1.8, 4, 0.17, 0.23)
    b_Kg_m = get_b(2.087, 2.850, 0.27, 0.28)
    # b_Kg_m2 = get_b(2.087, 2.208, 0.23, 0.25)
    b_L_m = get_b(25, 70, 0.24, 0.21)
    aa = 0.208 / (4.0 ** 0.38 * 0.779 ** 0.14 * 40.0 ** (-0.14) * 0.25 ** (-0.42))
    a = 1 / (np.exp(np.log(aa) / 0.38))

    b_ts_s = get_b(0.15, 0.3, 0.14, 0.097)
    b_S_s = get_b(1.8, 4, 0.099, 0.112)
    b_Kg_s = get_b(2.087, 2.850, 0.137, 0.145)
    b_L_s = get_b(25, 70, 0.135, 0.097)
    aa = 0.112 / (4.0 ** 0.14 * 0.779 ** 0.18 * 40.0 ** (-0.32) * 0.25 ** (-0.54))
    a = 1 / (np.exp(np.log(aa) / 0.014))

    sfile = "./one-lane-result.dat"
    mfile = "./multi-lane-result.dat"
    with open(sfile, 'r') as fid:
        txt = fid.readlines()
    one_res = []
    for line in txt:
        one_res.append(eval(line))
    one_res = pd.DataFrame(one_res)
    with open(mfile, 'r') as fid:
        txt = fid.readlines()
    multi_res = []
    for line in txt:
        multi_res.append(eval(line))
    multi_res = pd.DataFrame(multi_res)
    for i, row in multi_res.iterrows():
        g_my = DF_multi(row.S, row.L, row.Kg * 1.0e-12, row.ts)
        g_c = row.g
        # print(g_my, g_c)
    for i, row in one_res.iterrows():
        g_my = DF_one(row.S, row.L, row.Kg * 1.0e-12, row.ts)
        g_c = row.g
        print(g_my, g_c)
        ok = 1
