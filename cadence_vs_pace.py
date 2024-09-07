import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import seaborn

import strava_shared

seaborn.set()

runs = strava_shared.load_runs()

PLOT_STRIDE_LENGTH = False
PLOT_HEART_RATE = False  # todo :: could improve / separate visualization here
HIGHLIGHT_RUN = "latest"


def my_smooth(data, smooth_length=10):
    return np.array([
        np.mean(data[i:i+smooth_length])
        for i in range(len(data) - smooth_length)
    ])


plot_runs = runs[:50]


plt.figure(figsize=(12.8, 7.2))
for i, run in enumerate(plot_runs[::-1]):
    if PLOT_HEART_RATE and not run.heartrate:
        continue
    smooth_vel = my_smooth(run.velocity)
    smooth_cadence = my_smooth(run.cadence)
    plot_y_vals = (
        smooth_vel / (smooth_cadence / 60)
        if PLOT_STRIDE_LENGTH
        else my_smooth(run.heartrate)
        if PLOT_HEART_RATE
        else smooth_cadence
    )
    is_latest_run = i == len(plot_runs) - 1
    plt.scatter(
        smooth_vel,
        plot_y_vals,
        # color=matplotlib.cm.get_cmap("PiYG").reversed()(run.distance[-1] / 30000),
        color=(
            ("red" if is_latest_run else "black")
            if HIGHLIGHT_RUN == "latest"
            else None
        ),
        alpha=(
            (1 if is_latest_run else 0.03)
            if HIGHLIGHT_RUN == "latest"
            else 0.01
        ),
        s=3,
    )
    if len(plot_runs) <= 5:
        plt.plot(
            smooth_vel,
            plot_y_vals,
        )

plt.xlabel("velocity")
plt.ylabel(
    "stride length"
    if PLOT_STRIDE_LENGTH
    else "heart rate"
    if PLOT_HEART_RATE
    else "cadence"
)
plt.show()
