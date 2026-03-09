from collections import defaultdict

from matplotlib import pyplot as plt
import seaborn
import numpy as np

import strava_shared

activities = strava_shared.load_activities()

RECENT_N = 9999
RUN_INTERVAL_M = 200
SAMPLE_EVERY_N_START_POINTS = 10

for plot_me in [
    "velocity",
    "cadence",
    "heartrate",
]:
    data = defaultdict(list)
    for activity in activities[-RECENT_N:]:
        start_idx = 0
        while True:
            try:
                end_idx = next(
                    i
                    for i, d in enumerate(activity.distance)
                    if d > activity.distance[start_idx] + RUN_INTERVAL_M
                )
            except (StopIteration, IndexError):
                break
            data["velocity"].append(np.mean(activity.velocity[start_idx:end_idx]))
            data["cadence"].append(np.mean(activity.cadence[start_idx:end_idx]))
            if activity.heartrate is not None:
                data["heartrate"].append(np.mean(activity.heartrate[start_idx:end_idx]))
            start_idx += SAMPLE_EVERY_N_START_POINTS
    seaborn.set()
    plt.figure(figsize=(12.8, 7.2))
    seaborn.kdeplot(data[plot_me], cut=0)
    plt.xlabel(plot_me)
    plt.show()
