import numpy as np
from matplotlib import pyplot as plt

import strava_shared

runs = strava_shared.load_runs(require_cadences=False)

LENGTH_WEIGHTING = 1.5

max_len = max(run.distance[-1] for run in runs)

for run in runs:
    if not run.latlng:
        print(f"run missing latlng {run}, ignoring")
        continue
    plt.plot(
        *np.array(run.latlng).T[::-1],
        alpha=(
            (run.distance[-1] / max_len) ** LENGTH_WEIGHTING
            if LENGTH_WEIGHTING > 0
            else 0.2
        ),
    )
plt.show()
