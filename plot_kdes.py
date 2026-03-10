from matplotlib import pyplot as plt
import seaborn

import strava_shared

RECENT_N = 100
PLOT_CADENCE = True

activities = strava_shared.load_activities(latest_n=RECENT_N)

plt.figure(figsize=(12.8, 7.2))
if PLOT_CADENCE:
    plot_me = [activity.cadence for activity in activities]
    plt.xlabel("cadence")
else:
    plot_me = [activity.velocity for activity in activities]
    plt.xlabel("velocity")
seaborn.kdeplot(plot_me, cut=0)
plt.show()
