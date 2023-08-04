import json
import requests
import time
from pathlib import Path


ACCESS_TOKEN = (
    Path(__file__).parent / "secrets" / "latest_access.txt"
).read_text().strip()
STRAVA_RATE_CAP = 20  # actually 100; play safe for testing


# https://developers.strava.com/docs/reference/#api-models-StreamSet
ALL_STREAMS = [
    "time",
    "distance",
    "latlng",
    "altitude",
    "velocity_smooth",
    "heartrate",
    "cadence",
    # "watts",
    "temp",
    "moving",
    "grade_smooth",
]


def v3_api_call(api_call):
    return requests.get(
        f"https://www.strava.com/api/v3/{api_call}",
        headers={"Authorization": "Bearer " + ACCESS_TOKEN},
    ).json()


def get_activity_streams(activity_id):
    return v3_api_call(
        f"activities/{activity_id}/streams?"
        + "&".join("keys=" + key for key in ALL_STREAMS)
        + "&key_by_type",
    )


def get_activity_summaries():
    return v3_api_call(
        f"athlete/activities?before={int(time.time())}"
        f"&after=964796319&per_page=200",
    )


summaries = get_activity_summaries()
print("summaries:")
print(summaries)
print()

ids = [summary["id"] for summary in summaries]
print("ids:")
print(ids)
print()


START_ACTIVITY_IDX = 30
END_ACTIVITY_IDX = START_ACTIVITY_IDX + STRAVA_RATE_CAP - 10  # wiggle room

print(f"querying activites from {START_ACTIVITY_IDX} to {END_ACTIVITY_IDX}")

result = {}
for activity_id in ids[START_ACTIVITY_IDX:END_ACTIVITY_IDX]:
    print(f"retrieving {activity_id}")
    result[activity_id] = get_activity_streams(activity_id)

(
    Path(__file__).parent
    / f"streams_{START_ACTIVITY_IDX}_to_{END_ACTIVITY_IDX}.json"
).write_text(json.dumps(result))
