import numpy as np
from matplotlib import pyplot as plt

import strava_shared

runs = strava_shared.load_runs(require_cadences=False)

for run in runs:
    if not run.latlng:
        print(f"run missing latlng {run}, ignoring")
        continue
    plt.plot(
        *np.array(run.latlng).T[::-1],
        alpha=0.2,
    )
plt.show()
