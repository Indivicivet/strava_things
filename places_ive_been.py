import numpy as np
from matplotlib import pyplot as plt

import strava_shared

runs = strava_shared.load_runs(require_cadences=False)

for run in runs:
    plt.scatter(*np.array(run.latlng).T[::-1])
plt.show()
