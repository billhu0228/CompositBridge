import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
import pylab

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
def g(S, L, Kg, ts):
    return 0.06 + (S / 14) ** 0.4 * (S / L) ** 0.3 * (Kg / (12.0 * L * ts ** 3)) ** 0.01


# -------------------------------------------------------------------------------
fig = plt.figure(figsize=(6, 3.75))
ax = fig.add_axes([0.11, 0.13, 0.86, 0.82])
ax.grid(True, ls='dotted')
cv = FigureCanvas(fig)
ax.set_xlabel("x")
ax.set_ylabel("y")
Slist = np.linspace(3.5, 16, 10)
ret = [g(S, 80, 6e6, 5) for S in Slist]
ax.plot(Slist, ret, linewidth=1.75)
cv.print_figure('./S-g.png', dpi=300)
