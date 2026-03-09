import datetime
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import json

import gpxpy

MY_DATA_FOLDER = Path(__file__).parent / "my_data"


@dataclass(frozen=True)
class ActivityType:
    name: str

    @property
    def is_run(self) -> bool:
        return self.name in ("Run", "Trail Run")

    def __str__(self):
        return self.name


@dataclass
class Activity:
    activity_id: str
    velocity: list
    distance: list
    time: list
    cadence: list
    heartrate: Optional[list] = None
    latlng: Optional[list] = None
    date: Optional[datetime.datetime] = None
    activity_type: ActivityType = ActivityType("Run")


def load_activities(require_cadences=True):
    activities = []
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
            # old format, pre 2025-09ish: convert to dict layout
            streams = {s["type"]: s for s in streams}

        if isinstance(streams, dict):
            # unified format (dict of dicts)
            def _getdata(label):
                stream = streams.get(label)
                if stream is None:
                    return None
                return stream["data"]

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
            print(f"got an activity missing things, {p.stem=}, {require_cadences=}")
            continue
        activities.append(
            Activity(
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
                date=datetime.datetime.strptime(
                    info["metadata"]["start_date"], "%Y-%m-%dT%H:%M:%SZ"
                ).replace(tzinfo=datetime.timezone.utc),
                # ^todo :: proper timezone handling?
                activity_type=ActivityType(info["metadata"].get("type", "Run")),
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
        activities.append(
            Activity(
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
                latlng=[(point.latitude, point.longitude) for point in segment.points],
                date=gpx.time,
                # GPX doesn't easily store type in a standard way here:
                activity_type=ActivityType("Run"),
            ),
        )
    return sorted(activities, key=lambda r: r.date, reverse=True)
