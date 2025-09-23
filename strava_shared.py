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
        streams = info["streams"]
        if isinstance(streams, list):
            # old format, pre 2025-09ish
            for retrieved in streams:
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
        elif isinstance(streams, dict):

            def _getdata(label):
                stream = streams.get(label)
                if stream is None:
                    return None
                return stream["data"]

            # new format, 2025-09ish onwards
            this_velocities = _getdata("velocity_smooth")
            this_distances = _getdata("distance")
            this_times = _getdata("time")
            this_cadences = _getdata("cadence")
            this_hrs = _getdata("heartrate")
            this_latlng = _getdata("latlng")
        else:
            raise ValueError(f"unclear what is {streams=}, expected dict or list")
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
        distances = [0]
        for pt1, pt2 in zip(segment.points, segment.points[1:]):
            distances.append(distances[-1] + pt1.distance_3d(pt2))
        runs.append(
            Run(
                activity_id=p.stem.split("_")[1],
                velocity=None,  # todo
                distance=distances,
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
