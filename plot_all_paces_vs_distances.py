import datetime
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import seaborn
from tqdm import tqdm

seaborn.set()
plt.style.use("dark_background")

MY_DATA_FOLDER = Path(__file__).parent / "my_data"

all_data = {
    activity_id: data
    for p in MY_DATA_FOLDER.glob("*.json")
    for activity_id, data in json.loads(p.read_text()).items()
}


@dataclass
class Run:
    activity_id: str
    velocity: list
    distance: list
    time: list
    cadence: list
    heartrate: Optional[list] = None


runs = []
for activity_id, info in all_data.items():
    this_velocities = None
    this_distances = None
    this_times = None
    this_cadences = None
    this_hrs = None
    for retrieved in info:
        # todo :: wow this is awful. :)
        if retrieved["type"] == "velocity_smooth":
            this_velocities = retrieved["data"]
        if retrieved["type"] == "distance":
            this_distances = retrieved["data"]
        if retrieved["type"] == "time":
            this_times = retrieved["data"]
        if retrieved["type"] == "cadence":
            this_cadences = retrieved["data"]
        if retrieved["type"] == "heartrate":
            this_hrs = retrieved["data"]
    if (
        this_distances is not None
        and this_velocities is not None
        and this_times is not None
        and this_cadences is not None
    ):
        runs.append(
            Run(
                activity_id=activity_id,
                velocity=this_velocities,
                distance=this_distances,
                time=this_times,
                cadence=this_cadences,
                heartrate=this_hrs,
            )
        )
    else:
        print(f"got a run missing things, {activity_id=}")


#max_distance = max(run.distance[-1] for run in runs)
PLOT_DISTANCE_INTERVAL = 100


HR_MIN = 130
HR_MAX = 200


def hr_to_01(hr):
    return np.clip(
        (np.array(hr) - HR_MIN) / (HR_MAX - HR_MIN),
        0, 1
    )


color_map_from_01 = matplotlib.cm.get_cmap("RdYlBu").reversed()


def color_map(hr):
    return color_map_from_01(hr_to_01(hr))


for run in tqdm(runs[:5]):  # most recent
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
                delta_i = next(
                    i
                    for i, d in enumerate(run.distance[start_i + 1:])
                    if (d - start_d) > interval
                )
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
            interval_paces.append("7:00")
        else:
            interval_paces.append(datetime.datetime.utcfromtimestamp(
                shortest_time * 1000 / interval
            ))
        interval_hrs.append(hr)
    plt.plot(
        intervals,
        interval_paces,
        c=color_map(np.mean(interval_hrs, axis=0)),
    )
    plt.scatter(
        intervals,
        interval_paces,
        c=color_map(interval_hrs),
        s=20,
    )


color_scalar_mappable = plt.cm.ScalarMappable(
    cmap=color_map_from_01,
    norm=plt.Normalize(vmin=HR_MIN, vmax=HR_MAX),
)
color_scalar_mappable.set_array([])  # Empty array since we only need the colormap
cbar = plt.colorbar(color_scalar_mappable)


#plt.xscale("log")
start, end = plt.gca().get_xlim()
plt.gca().xaxis.set_ticks(range(0, int(end) + 1000, 1000))
plt.gca().yaxis.set_major_formatter(matplotlib.dates.DateFormatter("%M:%S"))
plt.gca().invert_yaxis()
plt.xlabel("distance")
plt.ylabel("pace (MM:SS / km)")
plt.show()
