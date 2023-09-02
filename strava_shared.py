from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import json


MY_DATA_FOLDER = Path(__file__).parent / "my_data"


@dataclass
class Run:
    activity_id: str
    velocity: list
    distance: list
    time: list
    cadence: list
    heartrate: Optional[list] = None
    latlng: Optional[list] = None


def load_runs():
    all_data = {
        activity_id: data
        for p in MY_DATA_FOLDER.glob("*.json")
        for activity_id, data in json.loads(p.read_text()).items()
    }
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
            if retrieved["type"] == "latlng":
                this_latlng = retrieved["data"]
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
                    # cadences are in cycles/min, I want spm
                    cadence=[2 * c for c in this_cadences],
                    heartrate=this_hrs,
                    latlng=this_latlng,
                )
            )
        else:
            print(f"got a run missing things, {activity_id=}")
    return runs
