from matplotlib import pyplot as plt
import numpy as np

import strava_shared

runs = strava_shared.load_runs()

measure_vals = [run.velocity for run in runs]
plt.scatter(
    [np.mean(seq) for seq in measure_vals],
    [np.var(seq) for seq in measure_vals],
    c=[run.distance[-1] for run in runs],
    alpha=np.clip([run.distance[-1]/10000 for run in runs], 0, 1),
    s=[run.distance[-1]/100 for run in runs],
)
plt.xlabel("mean")
plt.ylabel("variance")
plt.colorbar()
plt.show()
