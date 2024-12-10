from collections import defaultdict

from matplotlib import pyplot as plt
import seaborn
import numpy as np

import strava_shared

runs = strava_shared.load_runs()

RECENT_N = 100
RUN_INTERVAL_M = 1000
SAMPLE_EVERY_N_START_POINTS = 10

PLOT_ME = "velocity"

use_runs = runs[-RECENT_N:]

data = defaultdict(list)
for run in runs:
    start_idx = 0
    while True:
        try:
            end_idx = next(
                i
                for i, d in enumerate(run.distance)
                if d > run.distance[start_idx] + RUN_INTERVAL_M
            )
        except StopIteration:
            break
        data["velocity"].append(np.mean(run.velocity[start_idx:end_idx]))
        data["cadence"].append(np.mean(run.cadence[start_idx:end_idx]))
        if run.heartrate is not None:
            data["heartrate"].append(np.mean(run.heartrate[start_idx:end_idx]))
        start_idx += SAMPLE_EVERY_N_START_POINTS

seaborn.set()
plt.figure(figsize=(12.8, 7.2))
seaborn.kdeplot(data[PLOT_ME], cut=0)
plt.xlabel(PLOT_ME)
plt.legend()
plt.show()
