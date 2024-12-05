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
plt.legend()
plt.show()

