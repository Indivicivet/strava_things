"""
old script, slightly jank - velocity over heart rate
"""


import numpy as np
from tqdm import tqdm

import strava_shared

activities = strava_shared.load_activities(require_cadences=False)

hard_activities = []

for activity in tqdm(activities):
    if activity.heartrate is None or activity.distance[-1] <= 5000:
        continue
    if np.max(activity.heartrate) > 150:
        hard_activities.append(
            (activity.date, np.mean(activity.velocity) / np.mean(activity.heartrate))
        )

# Sort by date (already sorted by load_activities, but just in case)
hard_activities.sort(key=lambda x: x[0])

print("velocity over heart rate")
for date, ratio in hard_activities:
    date_str = date.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{date_str}, {100 * ratio:.2f}%")
