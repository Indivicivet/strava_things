import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import seaborn

import strava_shared

seaborn.set()

runs = strava_shared.load_runs()

PLOT_STRIDE_LENGTH = False


def my_smooth(data, smooth_length=30):
    return np.array([
        np.mean(data[i:i+smooth_length])
        for i in range(len(data) - smooth_length)
    ])


plot_runs = runs[:5]


for run in plot_runs:
    smooth_vel = my_smooth(run.velocity)
    smooth_cadence = my_smooth(run.cadence)
    plot_y_vals = (
        smooth_vel / (smooth_cadence / 60)
        if PLOT_STRIDE_LENGTH
        else smooth_cadence
    )
    plt.scatter(
        smooth_vel,
        plot_y_vals,
        # color=matplotlib.cm.get_cmap("PiYG").reversed()(run.distance[-1] / 30000),
        alpha=0.1,
        s=3,
    )
    if len(plot_runs) <= 5:
        plt.plot(
            smooth_vel,
            plot_y_vals,
        )

plt.xlabel("velocity")
plt.ylabel("stride length" if PLOT_STRIDE_LENGTH else "cadence")
plt.show()
