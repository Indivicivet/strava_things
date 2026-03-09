from matplotlib import pyplot as plt
import numpy as np

import strava_shared

activities = strava_shared.load_activities()

PLOT_CADENCE = False

plt.figure(figsize=(12.8, 7.2))
if PLOT_CADENCE:
    measure_vals = [activity.cadence for activity in activities]
    plt.title("cadence")
else:
    measure_vals = [activity.velocity for activity in activities]
    plt.title("velocity")
dist_arr = np.array([activity.distance[-1] for activity in activities])
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
