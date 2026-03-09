import numpy as np
from matplotlib import pyplot as plt

import strava_shared

activities = strava_shared.load_activities(require_cadences=False)

LENGTH_WEIGHTING = 1.5

max_len = max(activity.distance[-1] for activity in activities)

for activity in activities:
    if not activity.latlng:
        print(f"activity missing latlng {activity}, ignoring")
        continue
    plt.plot(
        *np.array(activity.latlng).T[::-1],
        alpha=(
            (activity.distance[-1] / max_len) ** LENGTH_WEIGHTING
            if LENGTH_WEIGHTING > 0
            else 0.2
        ),
    )
plt.show()
