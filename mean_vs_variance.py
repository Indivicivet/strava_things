from matplotlib import pyplot as plt
import numpy as np

import strava_shared

runs = strava_shared.load_runs()

PLOT_CADENCE = False

plt.figure(figsize=(12.8, 7.2))
if PLOT_CADENCE:
    measure_vals = [run.cadence for run in runs]
    plt.title("cadence")
else:
    measure_vals = [run.velocity for run in runs]
    plt.title("velocity")
dist_arr = np.array([run.distance[-1] for run in runs])
plt.scatter(
    [np.mean(seq) for seq in measure_vals],
    [np.var(seq) for seq in measure_vals],
    c=dist_arr,
    alpha=np.clip(dist_arr / 10000, 0, 1),
    s=dist_arr / 100,
)
plt.xlabel("mean")
plt.ylabel("variance")
colorbar = plt.colorbar()
colorbar.set_label("distance")
plt.show()
