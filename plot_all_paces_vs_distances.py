import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from matplotlib import pyplot as plt
import seaborn
from tqdm import tqdm

seaborn.set()

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

for run in tqdm(runs):
    intervals = range(
        PLOT_DISTANCE_INTERVAL * 2,
        int(run.distance[-1]),
        PLOT_DISTANCE_INTERVAL,
    )
    interval_speeds = []
    for interval in intervals:
        shortest_time = 9999
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
                shortest_time = min(
                    shortest_time,
                    run.time[start_i + delta_i] - run.time[start_i],
                )
        if shortest_time == 0:
            print(f"shortest_time is zero!?")
            interval_speeds.append(0)
        else:
            interval_speeds.append(interval / shortest_time)
    plt.plot(intervals, interval_speeds)

#plt.xscale("log")
start, end = plt.gca().get_xlim()
plt.gca().xaxis.set_ticks(range(0, int(end) + 1000, 1000))
plt.ylabel("velocity")
plt.xlabel("distance")
plt.show()
