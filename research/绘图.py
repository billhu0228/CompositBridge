import pylab
import pandas as pd
import matplotlib.pyplot as plt
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


def plot_fig(one_range, multi_range, col, x_label, xfactor=1.0):
    fig = plt.figure(figsize=(4, 3))
    ax = fig.add_axes([0.13, 0.13, 0.85, 0.75])
    ax.grid(True, ls='dotted')
    cv = FigureCanvas(fig)
    ax.set_xlabel(x_label)
    ax.set_ylabel("车道分配系数 g")
    xs = one_res.iloc[one_range[0]:one_range[1]][col] * xfactor
    ys = one_res.iloc[one_range[0]:one_range[1]].g
    ax.plot(xs, ys, linewidth=1.75, marker='v', label="单车道-弯矩",ls='--')
    # for i, j in zip(xs, ys):
    #     ax.annotate("(%.3f,%.3f)" % (i, j), xy=(i, j), size=6, rotation=90)
    xs = multi_res.iloc[multi_range[0]:multi_range[1]][col] * xfactor
    ys = multi_res.iloc[multi_range[0]:multi_range[1]].g
    ax.plot(xs, ys, linewidth=1.75, marker='^', label="多车道-弯矩",ls='-')
    # for i, j in zip(xs, ys):
    #     ax.annotate("(%.3f,%.3f)" % (i, j), xy=(i, j), size=6, rotation=90)
    ax.set_ylim([0, 0.4])
    hds, labs = ax.get_legend_handles_labels()
    ax.legend(hds, labs, loc='upper left', bbox_to_anchor=(0.0, 1.15), ncol=2, fancybox=False, shadow=False, numpoints=1)
    cv.print_figure('../../01 Latex/pic/one-lane-%s.png' % col, dpi=300)


if __name__ == "__main__":
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

    plot_fig((4, 8), (21, 25), col='S', x_label="主梁间距 S(m)")
    plot_fig((21, 26), (15, 20), col='Kg', x_label="主梁刚度 Kg(m$^4$)", xfactor=1.e-12)
    plot_fig((9, 19), (6, 13), col='L', x_label="计算跨度 L(m)")
    plot_fig((35, 39), (25, 29), col='ts', x_label="预制板厚度 Ts(m)")
    plot_fig((31, 35), (34, 38), col='Hc', x_label="横梁高度 H$_c$(m)")
    plot_fig((39, 44), (30, 35), col='nspan', x_label="跨数 n")
