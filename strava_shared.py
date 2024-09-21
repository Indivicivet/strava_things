import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import json

import gpxpy

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
    runs = []
    for p in MY_DATA_FOLDER.glob("*.json"):
        info = json.loads(p.read_text())
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
            this_distances is None
            or this_velocities is None
            or this_times is None
            or (this_cadences is None and require_cadences)
        ):
            print(f"got a run missing things, {p.stem=}, {require_cadences=}")
            continue
        runs.append(
            Run(
                activity_id=p.stem.split("_")[1],
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
                ).replace(tzinfo=datetime.timezone.utc),
                # ^todo :: proper timezone handling?
            )
        )
    for p in MY_DATA_FOLDER.glob("*.gpx"):
        with open(p) as f:
            gpx = gpxpy.parse(f)
        if len(gpx.tracks) > 1:
            print(f"{len(gpx.tracks)=} > 1, only using first")
        track = gpx.tracks[0]
        if len(track.segments) > 1:
            print(f"{len(track.segments)=} > 1, only using first")
        segment = track.segments[0]
        runs.append(
            Run(
                activity_id=p.stem.split("_")[1],
                velocity=None,  # todo
                distance=None,  # todo
                time=[point.time for point in segment.points],
                # cadences are in cycles/min, I want spm
                cadence=[
                    2 * int(point.extensions[0].getchildren()[1].text)
                    for point in segment.points
                ],
                # todo :: these could probs do with being more robust
                heartrate=[
                    int(point.extensions[0].getchildren()[0].text)
                    for point in segment.points
                ],
                latlng=[
                    (point.latitude, point.longitude)
                    for point in segment.points
                ],
                date=gpx.time,
            ),
        )
    return sorted(runs, key=lambda r: r.date, reverse=True)
