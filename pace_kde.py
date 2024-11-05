from matplotlib import pyplot as plt
import numpy as np
import seaborn

import strava_shared

runs = strava_shared.load_runs()

seaborn.kdeplot(
    [run.velocity for run in runs],
)
plt.xlabel("velocity")
plt.show()
