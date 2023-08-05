import json
from pathlib import Path

from matplotlib import pyplot as plt

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
    plt.plot(this_distances, this_velocities)

plt.show()
