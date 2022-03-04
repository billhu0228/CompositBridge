from src.mechanics import calculate
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import pylab

# -------------------------------------------------------------------------------
# 绘图参数设置
# -------------------------------------------------------------------------------
pylab.mpl.rcParams['font.sans-serif'] = ['SimHei']
pylab.mpl.rcParams['axes.unicode_minus'] = False
pylab.mpl.rcParams['font.size'] = 8
pylab.mpl.rcParams['legend.fontsize'] = u'small'
pylab.mpl.rcParams['xtick.labelsize'] = u'small'
pylab.mpl.rcParams['ytick.labelsize'] = u'small'
L = [69, 69,69]
xs = [a for a in range(sum(L) + 1)]
# r = calculate([L, L, L], cForce=[10, 20], moment_loc=xs)
r = calculate(L,
              # cForce=[25],
              dForce=[[0, sum(L)]],
              moment_loc=xs, shear_loc=xs)

fig = plt.figure(figsize=(6, 3.5))
cv = FigureCanvas(fig)
ax = fig.add_axes([0.12, 0.13, 0.84, 0.4])
ax2 = fig.add_axes([0.12, 0.53, 0.84, 0.4])
ax.grid(True)
ax2.grid(True)
ax.plot(xs, r['m'], 'k', linewidth=0.5, label=u'弯矩')
ax2.plot(xs, r['s'], 'k', linewidth=0.5, label=u'剪力')
hr = [-1.25]
for y in hr:
    ax.plot([0, 150], [y, y], ls='dashed', label=str(y))
hds, labs = ax.get_legend_handles_labels()
ax.legend(hds, labs, fancybox=True, shadow=True, numpoints=1)

ax2.xaxis.set_ticks_position('top')

cv.print_figure('moment.png', dpi=300)

plt.close('all')

# L = 20
# F = 1
# M_from_equ = 0.156 * F * L
# print(M_from_equ)
# print(r)
