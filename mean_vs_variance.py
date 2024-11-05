from matplotlib import pyplot as plt
import numpy as np

import strava_shared

runs = strava_shared.load_runs()

measure_vals = [run.velocity for run in runs]
plt.scatter(
    [np.mean(seq) for seq in measure_vals],
    [np.var(seq) for seq in measure_vals],
)
plt.xlabel("mean")
plt.ylabel("variance")
plt.show()
