from src.CompositeBridge.tools import read_res, read_node_res
import matplotlib.pyplot as plt
import numpy as np
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
fig = plt.figure(figsize=(6, 3.75))
ax = fig.add_axes([0.11, 0.13, 0.86, 0.82])
ax.grid(True, ls='dotted')
cv = FigureCanvas(fig)
ax.set_xlabel("x")
ax.set_ylabel("my")

filepath = r"E:\20220217 组合梁论文\02 Python\bin\Model3\liveload.res"
# rr = read_node_res(filepath)
rr = read_res(filepath)
filter2 = rr.load_node == 397
for zz in [1.2, 5.2, 9.2, 13.2]:
    filter1 = rr.z == zz
    out = rr[filter1 & filter2]
    ax.plot(out.x, out.sfz, linewidth=1.75)
cv.print_figure('./M-Φ曲线.png', dpi=300)

f = 1
