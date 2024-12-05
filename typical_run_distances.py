"""
KDE for run distances
"""

from matplotlib import pyplot as plt
import seaborn

import strava_shared

runs = strava_shared.load_runs()

RECENT_N = 100

plt.figure(figsize=(12.8, 7.2))
seaborn.kdeplot(
    [run.distance[-1] for run in runs],
    cut=0,
)
plt.xlabel("run length (m)")
plt.show()

