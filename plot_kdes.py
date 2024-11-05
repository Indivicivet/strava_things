from matplotlib import pyplot as plt
import numpy as np
import seaborn

import strava_shared

runs = strava_shared.load_runs()

RECENT_N = 100
PLOT_CADENCE = True

use_runs = runs[-RECENT_N:]

if PLOT_CADENCE:
    plot_me = [run.cadence for run in use_runs]
    plt.xlabel("cadence")
else:
    plot_me = [run.velocity for run in use_runs]
    plt.xlabel("velocity")
seaborn.kdeplot(plot_me)
plt.show()
