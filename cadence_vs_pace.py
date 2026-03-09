import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import seaborn
from tqdm import tqdm

import strava_shared

seaborn.set()

activities = strava_shared.load_activities()

PLOT_STRIDE_LENGTH = False
PLOT_HEART_RATE = False  # todo :: could improve / separate visualization here
LAST_N = 50
PLOT_SCATTER = True
PLOT_KDE = True
KDE_BASED_ON_DISTANCE = True

# filters for velocity and cadence stability
VELOCITY_STD_THRESHOLD = 0.5
CADENCE_STD_THRESHOLD = 5

HIGHLIGHT_ACTIVITY = "latest"  # "latest" or None or an activity id


def my_smooth(data, smooth_length=10):
    return np.array(
        [np.mean(data[i : i + smooth_length]) for i in range(len(data) - smooth_length)]
    )


def std_if_valid(window_data, invalid_thres):
    return 9999 if any(x < invalid_thres for x in window_data) else np.std(window_data)


def window_std(data, window=10, invalid_thres=80):
    return np.array(
        [
            std_if_valid(data[i : i + window], invalid_thres)
            for i in range(len(data) - window)
        ]
    )


def pace_formatter(x, pos):
    if x <= 0:
        return ""
    pace_seconds = 1000 / x
    return f"{int(pace_seconds // 60)}:{int(pace_seconds % 60):02d}"


plot_activities = activities[:LAST_N]

# only used for kde plot
all_vels = []
all_y_vals = []
all_weights = []

plt.figure(figsize=(12.8, 7.2))
for i, activity in enumerate(tqdm(plot_activities[::-1])):
    if PLOT_HEART_RATE and not activity.heartrate:
        continue
    smooth_vel = my_smooth(activity.velocity)
    smooth_cadence = my_smooth(activity.cadence)
    plot_y_vals = np.array(
        smooth_vel / (smooth_cadence / 60)
        if PLOT_STRIDE_LENGTH
        else (
            np.array(my_smooth(activity.heartrate))
            if PLOT_HEART_RATE
            else smooth_cadence
        )
    )
    mask = (
        window_std(activity.velocity, invalid_thres=0.2) < VELOCITY_STD_THRESHOLD
    ) & (window_std(activity.cadence, invalid_thres=80) < CADENCE_STD_THRESHOLD)

    smooth_vel = smooth_vel[mask]
    plot_y_vals = plot_y_vals[mask]

    highlight_this_activity = (
        i == len(plot_activities) - 1
        if HIGHLIGHT_ACTIVITY == "latest"
        else (
            activity.activity_id == str(HIGHLIGHT_ACTIVITY)
            if HIGHLIGHT_ACTIVITY is not None
            else False
        )
    )
    if PLOT_KDE:
        # plot at the end
        all_vels = np.append(all_vels, smooth_vel)
        all_y_vals = np.append(all_y_vals, plot_y_vals)
        all_weights = np.append(
            all_weights,
            smooth_vel if KDE_BASED_ON_DISTANCE else np.ones(len(smooth_vel)),
        )
    if (PLOT_SCATTER or highlight_this_activity) and len(smooth_vel) > 0:
        plt.scatter(
            smooth_vel,
            plot_y_vals,
            # color=matplotlib.cm.get_cmap("PiYG").reversed()(activity.distance[-1] / 30000),
            color=(
                ("red" if highlight_this_activity else "black")
                if HIGHLIGHT_ACTIVITY
                else None
            ),
            alpha=(
                (1 if highlight_this_activity else 0.03) if HIGHLIGHT_ACTIVITY else 0.01
            ),
            s=3,
        )
        if len(plot_activities) <= 5:
            plt.plot(
                smooth_vel,
                plot_y_vals,
            )

if PLOT_KDE:
    print("Plotting KDE...")
    seaborn.kdeplot(
        x=all_vels,
        y=all_y_vals,
        weights=all_weights,
        levels=15,
        # fill=True,  # n.b. would have to redraw highlighted activity after
    )

plt.gca().xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(pace_formatter))
plt.xlabel("pace (min/km)")
plt.ylabel(
    "stride length"
    if PLOT_STRIDE_LENGTH
    else "heart rate" if PLOT_HEART_RATE else "cadence"
)
plt.show()
