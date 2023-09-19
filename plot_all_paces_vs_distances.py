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

runs = strava_shared.load_runs(require_cadences=False)

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


START_DISTANCE_IDX = 2
for run in tqdm(runs[:50]):  # most recent
    intervals = range(
        PLOT_DISTANCE_INTERVAL * START_DISTANCE_IDX,
        int(run.distance[-1]) + 1,
        PLOT_DISTANCE_INTERVAL,
    )
    shortest_times = [9999] * len(intervals)
    shortest_time_hrs = [100] * len(intervals)
    for start_i, start_d in enumerate(run.distance):
        for latter_i, latter_d in enumerate(run.distance):
            if latter_i <= start_i:
                continue  # easiest way to code it up. probs not 2slow.
            interval_time = run.time[latter_i] - run.time[start_i]
            arr_idx = (
                int((latter_d - start_d) / PLOT_DISTANCE_INTERVAL)
                - START_DISTANCE_IDX
            )
            if arr_idx < 0:
                continue
            if interval_time < shortest_times[arr_idx]:
                shortest_times[arr_idx] = interval_time
                if run.heartrate is not None:
                    shortest_time_hrs[arr_idx] = sum(
                        run.heartrate[start_i:latter_i]
                    ) / (latter_i - start_i)
    interval_paces = [
        datetime.datetime.fromtimestamp(
            shortest_time * 1000 / interval
        )
        for interval, shortest_time in zip(intervals, shortest_times)
    ]
    if PLOT_TOPLINES_ONLY:
        for datetime_cutoff, data in topline_values.items():
            if run.date >= datetime_cutoff:
                continue
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
            interval_hrs = np.append(shortest_time_hrs, [0] * max(-need_extend_by, 0))
            where_update = interval_paces < data["paces"]
            data["paces"][where_update] = interval_paces[where_update]
            data["hrs"][where_update] = interval_hrs[where_update]
    if not PLOT_TOPLINES_ONLY:
        plt.plot(
            shortest_time_hrs if JUST_PLOT_HRS else intervals,
            interval_paces,
            c=color_map(np.mean(shortest_time_hrs, axis=0)),
        )
        plt.scatter(
            shortest_time_hrs if JUST_PLOT_HRS else intervals,
            interval_paces,
            c=color_map(shortest_time_hrs),
            s=20,
        )


if PLOT_TOPLINES_ONLY:
    for datetime_cutoff, data in topline_values.items():
        if len(data["paces"]) > len(data["intervals"]):
            # todo :: idk why this is needed;
            # hrs and paces seem consistent but intervals not; bad code.
            data["intervals"] = (2 + np.arange(len(data["paces"]))) * (
                PLOT_DISTANCE_INTERVAL
            )
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
            label=f"before {datetime_cutoff}",
        )
        plt.legend()


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
