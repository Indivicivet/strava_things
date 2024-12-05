"""
KDE for run distances
"""

from matplotlib import pyplot as plt
import seaborn

import strava_shared

runs = strava_shared.load_runs()

RECENT_N = 100

seaborn.set()
plt.figure(figsize=(12.8, 7.2))
seaborn.kdeplot(
    [run.distance[-1] for run in runs],
    cut=0,
    bw_adjust=0.15,
    label="slightly smoothed",
)
seaborn.kdeplot(
    [run.distance[-1] for run in runs],
    cut=0,
    bw_adjust=2,
    label="smooth",
)
plt.xlabel("run length (m)")
run_ticks = range(0, int(max(run.distance[-1] for run in runs) + 1), 1000)
plt.xticks(
    ticks=run_ticks,
    labels=[
        x if x % 5000 == 0 else ""
        for x in run_ticks
    ]
)
plt.legend()
plt.show()

