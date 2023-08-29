from matplotlib import pyplot as plt
import numpy as np

import strava_shared

runs = strava_shared.load_runs()


def my_smooth(data, smooth_length=20):
    return [
        np.mean(data[i:i+smooth_length])
        for i in range(len(data) - smooth_length)
    ]


for run in runs:
    plt.scatter(my_smooth(run.velocity), my_smooth(run.cadence), alpha=0.1, s=3)

plt.xlabel("velocity")
plt.ylabel("cadence")
plt.show()
