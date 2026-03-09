from matplotlib import pyplot as plt
import seaborn

import strava_shared

activities = strava_shared.load_activities()

RECENT_N = 100
PLOT_CADENCE = True

use_activities = activities[-RECENT_N:]

plt.figure(figsize=(12.8, 7.2))
if PLOT_CADENCE:
    plot_me = [activity.cadence for activity in use_activities]
    plt.xlabel("cadence")
else:
    plot_me = [activity.velocity for activity in use_activities]
    plt.xlabel("velocity")
seaborn.kdeplot(plot_me, cut=0)
plt.show()
