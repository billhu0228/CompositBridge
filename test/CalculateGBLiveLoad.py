import pandas as pd

from src.CompositeBridge.tools import read_res, read_node_res, get_effect_matrix, get_envo, get_value
from src.CompositeBridge import CompositeBridge
import matplotlib.pyplot as plt
import numpy as np
import pickle
import pylab
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

# -------------------------------------------------------------------------------
# 绘图参数设置
# -------------------------------------------------------------------------------
pylab.mpl.rcParams['font.sans-serif'] = ['SimHei']
pylab.mpl.rcParams['axes.unicode_minus'] = False
pylab.mpl.rcParams['font.size'] = 10
pylab.mpl.rcParams['legend.fontsize'] = u'small'
pylab.mpl.rcParams['xtick.labelsize'] = u'small'
pylab.mpl.rcParams['ytick.labelsize'] = u'small'


# -------------------------------------------------------------------------------

if __name__ == "__main__":
    modelName = "M2"
    with open("../bin/%s/bridge.pickle" % modelName, 'rb') as f:
        Bridge: CompositeBridge = pickle.load(f)
    filepath = "../bin/%s/liveload.res" % modelName
    rr = read_res(filepath)
    for girderZ in [1.2, 5.9, 10.6, 15.3]:
        my_x, sfz_x, fts = get_effect_matrix(rr, lane_num=1, grider_loc=girderZ, bridge=Bridge)
        lane1_my = get_envo(my_x, 'my', fts[0], fts[1], fts[2], 1.0)
        lane1_sfz = get_envo(sfz_x, 'sfz', fts[0], fts[1], fts[2], 1.2)
        fig = plt.figure(figsize=(6, 3.75))
        ax = fig.add_axes([0.11, 0.13, 0.86, 0.82])
        ax.grid(True, ls='dotted')
        cv = FigureCanvas(fig)
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.plot(lane1_my.x, lane1_my.my_max, linewidth=1.75)
        ax.plot(lane1_my.x, lane1_my.my_min, linewidth=1.75)
        vv = get_value(lane1_my[['x', 'my_min']], 21)
        cv.print_figure('./M-Φ曲线%i.png' % (girderZ * 10), dpi=300)
