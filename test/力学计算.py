import pandas as pd

from src.mechanics import calculate
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pylab
from CalculateGBLiveLoad import get_envo

# -------------------------------------------------------------------------------
# 绘图参数设置
# -------------------------------------------------------------------------------
pylab.mpl.rcParams['font.sans-serif'] = ['SimHei']
pylab.mpl.rcParams['axes.unicode_minus'] = False
pylab.mpl.rcParams['font.size'] = 8
pylab.mpl.rcParams['legend.fontsize'] = u'small'
pylab.mpl.rcParams['xtick.labelsize'] = u'small'
pylab.mpl.rcParams['ytick.labelsize'] = u'small'
L = [40]  # , 40, 40, 40]
xs = [a for a in range(sum(L) + 1)]
res = {'x': xs}
for x in xs:
    r = calculate(L, cForce=[x], moment_loc=xs, shear_loc=xs)
    res['my_%i' % x] = r['m']
res = pd.DataFrame(res)
kk = get_envo(res, 'my', 10500, 320000, 1, 1.0)
fig = plt.figure(figsize=(6, 3.75))
ax = fig.add_axes([0.11, 0.13, 0.86, 0.82])
ax.grid(True, ls='dotted')
cv = FigureCanvas(fig)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.set_ylim([-5300, 530])
ax.plot(kk.x, kk.my_max * 1e-3, linewidth=1.75)
ax.plot(kk.x, kk.my_min * 1e-3, linewidth=1.75)
cv.print_figure('./理论活载.png', dpi=300)
