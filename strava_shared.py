import datetime
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
    date: Optional[datetime.datetime] = None


def load_runs(require_cadences=True):
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
        this_latlng = None
        for retrieved in info["streams"]:
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
            and (this_cadences is not None or not require_cadences)
        ):
            runs.append(
                Run(
                    activity_id=activity_id,
                    velocity=this_velocities,
                    distance=this_distances,
                    time=this_times,
                    # cadences are in cycles/min, I want spm
                    cadence=(
                        [2 * c for c in this_cadences]
                        if this_cadences is not None
                        else None
                    ),
                    heartrate=this_hrs,
                    latlng=this_latlng,
                    date=datetime.datetime(
                        # todo :: should parse out the whole thing really eh?
                        *map(
                            int,
                            info["metadata"]["start_date"].split("T")[0].split("-"),
                        )
                    ),
                )
            )
        else:
            print(f"got a run missing things, {activity_id=}")
    return runs
