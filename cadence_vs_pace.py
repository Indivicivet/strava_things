import matplotlib
import datetime
from matplotlib import pyplot as plt
import numpy as np
import seaborn
from tqdm import tqdm

import strava_shared

seaborn.set()

runs = strava_shared.load_runs()

PLOT_STRIDE_LENGTH = False
PLOT_HEART_RATE = False  # todo :: could improve / separate visualization here
LAST_N = 500
PLOT_SCATTER = True
PLOT_KDE = True
KDE_BASED_ON_DISTANCE = True

# filters for velocity and cadence stability
VELOCITY_STD_THRESHOLD = 0.5
CADENCE_STD_THRESHOLD = 5

CUTOFF_DATE = datetime.datetime(2025, 1, 1, tzinfo=datetime.timezone.utc)

HIGHLIGHT_RUN = "latest"  # "latest" or None or an activity id


def my_smooth(data, smooth_length=10):
    return np.array(
        [np.mean(data[i : i + smooth_length]) for i in range(len(data) - smooth_length)]
    )


def std_if_valid(window_data, invalid_thres):
    return 9999 if any(x < invalid_thres for x in window_data) else np.std(window_data)


def window_std(data, window=10, invalid_thres=80):
    return np.array([
        std_if_valid(data[i : i + window], invalid_thres)
        for i in range(len(data) - window)
    ])



plot_runs = runs[:LAST_N]

# only used for kde plot
# format: [all_vels, all_y_vals, all_weights]
before_data = [[], [], []]
after_data = [[], [], []]

plt.figure(figsize=(12.8, 7.2))
for i, run in enumerate(tqdm(plot_runs[::-1])):
    if PLOT_HEART_RATE and not run.heartrate:
        continue
    smooth_vel = my_smooth(run.velocity)
    smooth_cadence = my_smooth(run.cadence)
    plot_y_vals = np.array(
        smooth_vel / (smooth_cadence / 60)
        if PLOT_STRIDE_LENGTH
        else np.array(my_smooth(run.heartrate)) if PLOT_HEART_RATE else smooth_cadence
    )
    mask = (window_std(run.velocity, invalid_thres=0.2) < VELOCITY_STD_THRESHOLD) & (
        window_std(run.cadence, invalid_thres=80) < CADENCE_STD_THRESHOLD
    )

    smooth_vel = smooth_vel[mask]
    plot_y_vals = plot_y_vals[mask]

    highlight_this_run = (
        i == len(plot_runs) - 1
        if HIGHLIGHT_RUN == "latest"
        else (
            run.activity_id == str(HIGHLIGHT_RUN)
            if HIGHLIGHT_RUN is not None
            else False
        )
    )
    if PLOT_KDE:
        # plot at the end
        data_to_append = after_data if run.date >= CUTOFF_DATE else before_data
        data_to_append[0] = np.append(data_to_append[0], smooth_vel)
        data_to_append[1] = np.append(data_to_append[1], plot_y_vals)
        data_to_append[2] = np.append(
            data_to_append[2],
            smooth_vel if KDE_BASED_ON_DISTANCE else np.ones(len(smooth_vel)),
        )
    if (PLOT_SCATTER or highlight_this_run) and len(smooth_vel) > 0:
        plt.scatter(
            smooth_vel,
            plot_y_vals,
            # color=matplotlib.cm.get_cmap("PiYG").reversed()(run.distance[-1] / 30000),
            color=("red" if highlight_this_run else "black") if HIGHLIGHT_RUN else None,
            alpha=(1 if highlight_this_run else 0.03) if HIGHLIGHT_RUN else 0.01,
            s=3,
        )
        if len(plot_runs) <= 5:
            plt.plot(
                smooth_vel,
                plot_y_vals,
            )

if PLOT_KDE:
    print("Plotting KDE...")
    if len(before_data[0]) > 0:
        seaborn.kdeplot(
            x=before_data[0],
            y=before_data[1],
            weights=before_data[2],
            levels=15,
            label="Before 2025-01-01",
            color="blue",
        )
    if len(after_data[0]) > 0:
        seaborn.kdeplot(
            x=after_data[0],
            y=after_data[1],
            weights=after_data[2],
            levels=15,
            label="After 2025-01-01",
            color="orange",
        )
    plt.legend()

plt.xlabel("velocity")
plt.ylabel(
    "stride length"
    if PLOT_STRIDE_LENGTH
    else "heart rate" if PLOT_HEART_RATE else "cadence"
)
plt.show()
