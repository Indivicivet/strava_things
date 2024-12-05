from matplotlib import pyplot as plt
import seaborn

import strava_shared

runs = strava_shared.load_runs()

RECENT_N = 100
PLOT_CADENCE = True

use_runs = runs[-RECENT_N:]

plt.figure(figsize=(12.8, 7.2))
if PLOT_CADENCE:
    plot_me = [run.cadence for run in use_runs]
    plt.xlabel("cadence")
else:
    plot_me = [run.velocity for run in use_runs]
    plt.xlabel("velocity")
seaborn.kdeplot(plot_me, cut=0)
plt.show()
