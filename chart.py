"""PPP of a basket rises linearly with its goods share (pppRate_eq_affine).
Uses calibrate.py: ICP 2021 PPPs and HCES 2022-23 Table A6 shares."""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from shares import load
from calibrate import split, ratio, model

d = load('./Table_A6.xlsx')
ga, sa = [], []
for sec in ('Rural', 'Urban'):
    g, s = split(d, sec, 'all'); ga += g; sa += s
RG, RS = ratio(ga), ratio(sa)
pts = {(sec, grp): model(d, sec, col, RG, RS)
       for sec in ('Rural', 'Urban') for grp, col in (('avg', 'all'), ('poor', 'b10'))}

INK, MUTED, GRID, BG = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
COL = {'avg': "#2a78d6", 'poor': "#eb6834"}
MARK = {'Rural': 'o', 'Urban': 's'}
NAME = {'avg': 'Average household', 'poor': 'Poorest 10%'}
MARGIN = 0.4                      # inches of blank space on every side

plt.rcParams.update({"font.family": "Inter", "font.size": 11})
fig, ax = plt.subplots(figsize=(8, 5.2), dpi=100)
fig.patch.set_facecolor(BG); ax.set_facecolor(BG)

ax.plot([0, 1], [RS, RG], color=MUTED, lw=2, zorder=2)
ax.text(0.03, RS - 1.3, f"all services: ₹{RS:.1f} per $", color=MUTED, fontsize=9.5)
ax.text(0.97, RG + 0.6, f"all goods: ₹{RG:.1f} per $", color=MUTED, fontsize=9.5, ha="right")

for (sec, grp), m in pts.items():
    ax.scatter([m['w']], [m['ppp']], s=95, marker=MARK[sec], color=COL[grp],
               edgecolor=BG, linewidth=2, zorder=4)

ARROW = dict(arrowstyle="-|>", color=INK, lw=1.2, mutation_scale=12)
for sec in ('Rural', 'Urban'):
    a, p = pts[(sec, 'avg')], pts[(sec, 'poor')]
    label = f"{sec}: +{100*(p['ppp']/a['ppp']-1):.1f}%"
    mid = (a['ppp'] + p['ppp']) / 2
    if sec == 'Rural':   # below the line: across from the average, then up to the poor
        ax.plot([a['w'], p['w']], [a['ppp'], a['ppp']], color=INK, lw=1.2, zorder=3)
        ax.annotate("", xy=(p['w'], p['ppp']), xytext=(p['w'], a['ppp']),
                    arrowprops=dict(**ARROW, shrinkA=0, shrinkB=8))
        ax.text(p['w'] + 0.02, mid, label, va="center", color=INK, fontsize=10)
    else:                # above the line: up from the average, then across to the poor
        ax.plot([a['w'], p['w']], [p['ppp'], p['ppp']], color=INK, lw=1.2, zorder=3)
        ax.annotate("", xy=(a['w'], p['ppp']), xytext=(a['w'], a['ppp']),
                    arrowprops=dict(**ARROW, shrinkA=8, shrinkB=0))
        ax.text(a['w'] - 0.02, mid, label, va="center", ha="right", color=INK, fontsize=10)

# legend: one entry per point, matching its colour and shape
h = [Line2D([], [], ls="", marker=MARK[s], ms=9, color=COL[g], label=f"{NAME[g]} ({s.lower()})")
     for s in ('Rural', 'Urban') for g in ('avg', 'poor')]
ax.legend(handles=h, loc="upper left", frameon=False, labelcolor=INK)

ax.set_xlim(0, 1); ax.set_ylim(10, 34)
ax.set_xlabel("Goods share of the basket, valued at US prices", color=INK)
ax.set_ylabel("PPP for the basket (₹ per $)", color=INK)
ax.set_title("The poor's PPP is higher because they buy relatively fewer services",
             loc="left", color=INK, fontsize=13, pad=12)
ax.grid(color=GRID, lw=0.8); ax.set_axisbelow(True)
for s in ax.spines.values(): s.set_color(GRID)
ax.tick_params(colors=MUTED)

# lay out the axes first, leaving a strip at the bottom for the source line
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.text(0.01, 0.01, "PPPs: ICP 2021. Shares: HCES 2022-23, Table A6. "
         "Central classification of mixed groups.", color=MUTED, fontsize=8)

# 'tight' crops to the drawn content; pad_inches then adds the same margin on every side
for name, dpi in (("ppp_chart.svg", None), ("ppp_chart.png", 240)):
    fig.savefig(name, dpi=dpi, facecolor=BG, bbox_inches="tight", pad_inches=MARGIN)
print("Saved ppp_chart.svg and ppp_chart.png")

