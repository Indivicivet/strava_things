"""
KDE for activity distances
"""

from matplotlib import pyplot as plt
import seaborn

import strava_shared

RUNS_ONLY = True

activities = strava_shared.load_activities()
if RUNS_ONLY:
    activities = [a for a in activities if a.activity_type.is_run]

RECENT_N = 100

seaborn.set()
plt.figure(figsize=(12.8, 7.2))
label_suffix = "runs" if RUNS_ONLY else "activities"

seaborn.kdeplot(
    [a.distance[-1] for a in activities],
    cut=0,
    bw_adjust=0.15,
    label=f"slightly smoothed {label_suffix}",
)
seaborn.kdeplot(
    [a.distance[-1] for a in activities],
    cut=0,
    bw_adjust=2,
    label=f"smooth {label_suffix}",
)
plt.xlabel(f"{label_suffix[:-1]} length (m)")
activity_ticks = range(0, int(max(a.distance[-1] for a in activities) + 1), 1000)
plt.xticks(
    ticks=activity_ticks, labels=[x if x % 5000 == 0 else "" for x in activity_ticks]
)
plt.legend()
plt.show()
