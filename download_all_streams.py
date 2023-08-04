import requests
import time
from pathlib import Path


ACCESS_TOKEN = (
    Path(__file__).parent / "secrets" / "latest_access.txt"
).read_text().strip()


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

for activity_id in ids:
    print(activity_id)
    print(get_activity_streams(activity_id))
    print()
