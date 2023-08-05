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

for activity_id, info in all_data.items():
    print(f"{activity_id=}")
    this_velocities = None
    this_distances = None
    for retrieved in info:
        if retrieved["type"] == "velocity_smooth":
            this_velocities = retrieved["data"]
        if retrieved["type"] == "distance":
            this_distances = retrieved["data"]
    if this_distances is None:
        print("no distances?")
        continue
    if this_velocities is None:
        print("no velocities?")
        continue
    average_velocity = sum(this_velocities) / len(this_velocities)
    plt.plot([0, max(this_distances)], [average_velocity] * 2)

plt.ylabel("velocity")
plt.xlabel("distance")
plt.show()
