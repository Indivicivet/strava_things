import json
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


velocity_and_distance = {}
for activity_id, info in all_data.items():
    this_velocities = None
    this_distances = None
    for retrieved in info:
        if retrieved["type"] == "velocity_smooth":
            this_velocities = retrieved["data"]
        if retrieved["type"] == "distance":
            this_distances = retrieved["data"]
    if this_distances is not None and this_velocities is not None:
        velocity_and_distance[activity_id] = {
            "velocity": this_velocities,
            "distance": this_distances,
        }

for _, data in velocity_and_distance.items():
    average_velocity = sum(data["velocity"]) / len(data["velocity"])
    plt.plot([0, max(data["distance"])], [average_velocity] * 2)

plt.ylabel("velocity")
plt.xlabel("distance")
plt.show()
