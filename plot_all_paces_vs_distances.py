import datetime
import time

import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import seaborn
from tqdm import tqdm

import strava_shared


seaborn.set()
plt.style.use("dark_background")

runs = strava_shared.load_runs()

#max_distance = max(run.distance[-1] for run in runs)
PLOT_DISTANCE_INTERVAL = 100

JUST_PLOT_HRS = False

HR_MIN = 130
HR_MAX = 200

PLOT_TOPLINES_ONLY = True
TOPLINE_DATE_CUTOFFS = [
    datetime.datetime(3000, 1, 1),
    datetime.datetime(2023, 7, 1),
    datetime.datetime(2023, 1, 1),
    datetime.datetime(2022, 7, 1),
]


def hr_to_01(hr):
    return np.clip(
        (np.array(hr) - HR_MIN) / (HR_MAX - HR_MIN),
        0, 1
    )


color_map_from_01 = matplotlib.cm.get_cmap("RdYlBu").reversed()


def color_map(hr):
    return color_map_from_01(hr_to_01(hr))


if PLOT_TOPLINES_ONLY:
    print("plotting toplines only")
    topline_values = {
        dt: {
            "paces": np.array([]),
            "hrs": np.array([]),
            "intervals": [],
        }
        for dt in TOPLINE_DATE_CUTOFFS
    }


for run in tqdm(runs[:50]):  # most recent
    intervals = range(
        PLOT_DISTANCE_INTERVAL * 2,
        int(run.distance[-1]),
        PLOT_DISTANCE_INTERVAL,
    )
    interval_paces = []
    interval_hrs = []
    for interval in intervals:
        shortest_time = 9999
        hr = 100
        for start_i, start_d in enumerate(run.distance):
            delta_i = None
            try:
                delta_i = max(next(
                    i
                    for i, d in enumerate(run.distance[start_i + 1:])
                    if (d - start_d) > interval
                ), 1)  # todo :: hacky way to avoid 0?
            except StopIteration:
                break
            else:
                interval_time = run.time[start_i + delta_i] - run.time[start_i]
                if interval_time < shortest_time:
                    shortest_time = interval_time
                    if run.heartrate is not None:
                        hr = sum(run.heartrate[start_i:][:delta_i]) / delta_i
        if shortest_time == 0:
            print(f"shortest_time is zero!?")
            interval_paces.append(datetime.datetime.fromtimestamp(
                7 * 60 * 1000 / interval  # 7min pace
            ))
        else:
            interval_paces.append(datetime.datetime.fromtimestamp(
                shortest_time * 1000 / interval
            ))
        interval_hrs.append(hr)
    if PLOT_TOPLINES_ONLY:
        for datetime_cutoff, data in topline_values.items():
            # todo :: need datetime in the run, eh? :)
            need_extend_by = len(interval_paces) - len(data["paces"])
            if need_extend_by > 0:
                data["paces"] = np.append(
                    data["paces"],
                    # todo :: ew. I'm doing silliness here, aren't I?
                    # (should store all as float then convert at the end for plot)
                    [datetime.datetime.fromtimestamp(99999)] * need_extend_by,
                )
                data["hrs"] = np.append(data["hrs"], [0] * need_extend_by)
                data["intervals"] = intervals
            # todo :: also kinda yucky code with this np array vs list business
            interval_paces = np.append(
                interval_paces,
                [datetime.datetime.fromtimestamp(99999)] * max(-need_extend_by, 0)
            )
            interval_hrs = np.append(interval_hrs, [0] * max(-need_extend_by, 0))
            where_update = interval_paces < data["paces"]
            data["paces"][where_update] = interval_paces[where_update]
            data["hrs"][where_update] = interval_hrs[where_update]
    if not PLOT_TOPLINES_ONLY:
        plt.plot(
            interval_hrs if JUST_PLOT_HRS else intervals,
            interval_paces,
            c=color_map(np.mean(interval_hrs, axis=0)),
        )
        plt.scatter(
            interval_hrs if JUST_PLOT_HRS else intervals,
            interval_paces,
            c=color_map(interval_hrs),
            s=20,
        )


if PLOT_TOPLINES_ONLY:
    for datetime_cutoff, data in topline_values.items():
        if not JUST_PLOT_HRS:
            plt.plot(
                data["intervals"],
                data["paces"],
            )
        plt.scatter(
            data["hrs"] if JUST_PLOT_HRS else data["intervals"],
            data["paces"],
            c=color_map(data["hrs"]),
            s=20,
        )
        break  # todo :: we don't actually use the datetime info yet.....


color_scalar_mappable = plt.cm.ScalarMappable(
    cmap=color_map_from_01,
    norm=plt.Normalize(vmin=HR_MIN, vmax=HR_MAX),
)
color_scalar_mappable.set_array([])  # Empty array since we only need the colormap
cbar = plt.colorbar(color_scalar_mappable)


#plt.xscale("log")
start, end = plt.gca().get_xlim()
if not JUST_PLOT_HRS:
    plt.gca().xaxis.set_ticks(range(0, int(end) + 1000, 1000))
plt.gca().yaxis.set_major_formatter(matplotlib.dates.DateFormatter("%M:%S"))
plt.gca().invert_yaxis()
plt.xlabel("HR" if JUST_PLOT_HRS else "distance")
plt.ylabel("pace (MM:SS / km)")
plt.show()
