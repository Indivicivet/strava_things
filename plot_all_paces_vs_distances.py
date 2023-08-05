import json
from dataclasses import dataclass
from pathlib import Path

from matplotlib import pyplot as plt
import seaborn

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


runs = []
for activity_id, info in all_data.items():
    this_velocities = None
    this_distances = None
    this_times = None
    for retrieved in info:
        if retrieved["type"] == "velocity_smooth":
            this_velocities = retrieved["data"]
        if retrieved["type"] == "distance":
            this_distances = retrieved["data"]
        if retrieved["type"] == "time":
            this_times = retrieved["data"]
    if (
        this_distances is not None
        and this_velocities is not None
        and this_times is not None
    ):
        runs.append(
            Run(
                activity_id=activity_id,
                velocity=this_velocities,
                distance=this_distances,
                time=this_times,
            )
        )

for run in runs:
    average_velocity = sum(run.velocity) / len(run.velocity)
    plt.plot([0, max(run.distance)], [average_velocity] * 2)

plt.ylabel("velocity")
plt.xlabel("distance")
plt.show()
