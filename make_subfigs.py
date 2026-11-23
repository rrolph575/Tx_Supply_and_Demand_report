import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from supply_and_demand_curve_with_subset_demand import plot_panel


figpath = 'figures/'

# Font sizes tuned for a 2x2 grid at figsize (16, 12)
plt.rcParams.update({
    'font.size': 18,
    'axes.labelsize': 18,
    'xtick.labelsize': 16,
    'ytick.labelsize': 16,
    'legend.fontsize': 15,
})

# Panel order is row-major to match the original layout:
#   top row = Aluminum (AC, MT), bottom row = Copper (AC, MT)
combos = [
    ('AC', 'aluminum'), ('MT', 'aluminum'),
    ('AC', 'copper'),   ('MT', 'copper'),
]
panel_labels = ['(a)', '(b)', '(c)', '(d)']
titles = ['Al (AC)', 'Al (MT)', 'Cu (AC)', 'Cu (MT)']

# End-use shares assumed for "All sectors demand" (bottom of bar = first entry).
# Each entry: (label, percent, shared category); '\n' in a label wraps it.
# The category sets the color,
# so equivalent end uses in the Al and Cu bars match.
end_use_shares = {
    'Al': [
        ('Transportation', 36, 'transportation'),
        ('Packaging', 23, 'packaging'),
        ('Buildings', 14, 'buildings'),
        ('Electrical', 9, 'electrical'),
        ('Consumer\nDurables', 8, 'consumer'),
        ('Machinery', 8, 'machinery'),
        ('Other', 2, 'other'),
    ],
    # Same category order as Al so the two bars stack in matching order
    'Cu': [
        ('Transportation\nEquipment', 18, 'transportation'),
        ('Building\nConstruction', 42, 'buildings'),
        ('Electrical and\nElectronic Products', 23, 'electrical'),
        ('Consumer and\nGeneral Products', 10, 'consumer'),
        ('Industrial Machinery\nand Equipment', 7, 'machinery'),
    ],
}
# Categorical palette: one fixed color per end-use category
category_colors = {
    'transportation': '#2a78d6',  # blue
    'packaging':      '#eb6834',  # orange
    'buildings':      '#1baf7a',  # aqua
    'electrical':     '#eda100',  # yellow
    'consumer':       '#e87ba4',  # magenta
    'machinery':      '#008300',  # green
    'other':          '#6250d6',  # violet
}

# Figure is widened from 16 in to 21 in; the 2x2 grid keeps its original
# physical size and the extra width on the right holds the assumptions box.
fig_w, fig_h = 21, 12
fig, axes = plt.subplots(2, 2, figsize=(fig_w, fig_h))
grid_left = 0.125 * 16 / fig_w
grid_right = grid_left + (0.9 - 0.125) * 16 / fig_w
plt.subplots_adjust(left=grid_left, right=grid_right, wspace=0.22, hspace=0.45)

for idx, ax in enumerate(axes.flat):
    scenario, material = combos[idx]
    show_ylabel = (idx % 2 == 0)  # ylabel on the left column only
    plot_panel(ax, scenario, material, show_ylabel=show_ylabel, show_legend=True)
    # bold panel label centered below each subplot
    ax.text(0.5, -0.32, f"{panel_labels[idx]} {titles[idx]}", transform=ax.transAxes,
            fontsize=18, fontweight='bold', va='top', ha='center', color='black')


def spread_labels(centers, heights):
    """Shift label y-positions apart so neighbouring labels (each heights[i]
    tall) don't overlap, keeping them close to their segment centers."""
    ys = list(centers)
    for _ in range(500):
        moved = False
        for i in range(1, len(ys)):
            min_gap = (heights[i - 1] + heights[i]) / 2
            overlap = min_gap - (ys[i] - ys[i - 1])
            if overlap > 1e-9:
                ys[i - 1] -= overlap / 2
                ys[i] += overlap / 2
                moved = True
        if not moved:
            break
    return ys


def draw_share_bar(bar_ax, shares, sublabel):
    """One vertical stacked bar of end-use shares, labelled to its right."""
    bottom = 0
    centers = []
    for name, pct, category in shares:
        bar_ax.bar(0, pct, bottom=bottom, width=1.0,
                   color=category_colors[category],
                   edgecolor='white', linewidth=2)
        centers.append(bottom + pct / 2)
        bottom += pct
    # ~8 bar units per text line at this font size, plus a little padding
    heights = [9 * (name.count('\n') + 1) + 1.5 for name, _, _ in shares]
    label_ys = spread_labels(centers, heights)
    for (name, pct, _), y_seg, y_lab in zip(shares, centers, label_ys):
        bar_ax.annotate(f"{name} ({pct}%)", xy=(0.5, y_seg), xytext=(1.6, y_lab),
                        va='center', ha='left', fontsize=17, color='black',
                        linespacing=1.1,
                        annotation_clip=False,
                        arrowprops=dict(arrowstyle='-', color='0.5', lw=0.8,
                                        shrinkA=2, shrinkB=0,
                                        connectionstyle='arc,angleA=180,'
                                        'angleB=0,armA=6,armB=6,rad=0'))
    bar_ax.set_xlim(-0.5, 0.5)
    bar_ax.set_ylim(0, 100)
    bar_ax.axis('off')
    bar_ax.set_title(sublabel, fontsize=20, fontweight='bold', pad=12)


# Assumptions panel (no outline): the region to the right of the grid
box_left, box_right = grid_right + 0.035, 0.995
top_pos = axes[0, 1].get_position()
box_top = top_pos.y1 + 0.075
box_center_x = (box_left + box_right) / 2
title = fig.text(box_center_x, top_pos.y1 + 0.015,
                 'Assumptions for\nAll Sectors Demand (USGS)',
                 ha='center', va='bottom', fontsize=20, fontweight='bold')

# Legend-style line sample to the left of the title, styled like the
# "All sectors demand (USGS)" line in the panels, so the box reads as its key.
# The sample + title are centered together over the assumptions column.
_inv = fig.transFigure.inverted()
_tb = _inv.transform(title.get_window_extent(fig.canvas.get_renderer()))
title_w = _tb[1, 0] - _tb[0, 0]
title_mid_y = (_tb[0, 1] + _tb[1, 1]) / 2
sample_len, sample_gap = 0.035, 0.008
group_left = box_center_x - (sample_len + sample_gap + title_w) / 2
title.set_x(group_left + sample_len + sample_gap + title_w / 2)
fig.add_artist(Line2D([group_left, group_left + sample_len],
                      [title_mid_y, title_mid_y], transform=fig.transFigure,
                      color='orange', linestyle=':', linewidth=3.5))

# Each bar is vertically aligned with its row of subplots. Both bars share
# one x position, chosen so the widest bar+labels group is centered in the box.
bar_w = 0.025
bar_axes = []
for row, (sublabel, shares) in enumerate(end_use_shares.items()):
    pos = axes[row, 1].get_position()
    bar_ax = fig.add_axes([box_left, pos.y0, bar_w, pos.height * 0.88])
    draw_share_bar(bar_ax, shares, sublabel)
    bar_axes.append(bar_ax)

renderer = fig.canvas.get_renderer()
inv = fig.transFigure.inverted()
group_right = max(
    inv.transform(t.get_window_extent(renderer))[1, 0]
    for bar_ax in bar_axes for t in bar_ax.texts
)
group_width = group_right - box_left
bar_x = box_center_x - group_width / 2
for bar_ax in bar_axes:
    p = bar_ax.get_position()
    bar_ax.set_position([bar_x, p.y0, p.width, p.height])

# Save both raster and true-vector versions
plt.savefig(f"{figpath}supply_demand_combined.png", bbox_inches='tight', dpi=300)
plt.savefig(f"{figpath}supply_demand_combined.svg", bbox_inches='tight')
plt.show()
