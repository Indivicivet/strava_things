import json
import requests
import time
from pathlib import Path

from tqdm import tqdm


ACCESS_TOKEN = (
    Path(__file__).parent / "secrets" / "latest_access.txt"
).read_text().strip()
MY_DATA_FOLDER = Path(__file__).parent / "my_data"
MY_DATA_FOLDER.mkdir(exist_ok=True, parents=True)
STRAVA_RATE_CAP = 100  # actually 100; play safe for testing


class RequestHadError(Exception):
    pass


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
    result = requests.get(
        f"https://www.strava.com/api/v3/{api_call}",
        headers={"Authorization": "Bearer " + ACCESS_TOKEN},
    ).json()
    if "errors" in result:
        raise RequestHadError(result)
    return result


def get_activity_streams(activity_id):
    return v3_api_call(
        f"activities/{activity_id}/streams?"
        + "keys=" + ",".join(ALL_STREAMS)
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


START_ACTIVITY_IDX = 0
END_ACTIVITY_IDX = START_ACTIVITY_IDX + STRAVA_RATE_CAP - 10  # wiggle room

print(f"querying activites from {START_ACTIVITY_IDX} to {END_ACTIVITY_IDX}")

result = {}
for idx in tqdm(range(START_ACTIVITY_IDX, END_ACTIVITY_IDX)):
    try:
        activity_id = summaries[idx]["id"]
        tqdm.write(f"retrieving {activity_id}")
        result[activity_id] = {
            "metadata": summaries[idx],
            "streams": get_activity_streams(activity_id),
        }
    except (RequestHadError, IndexError) as e:
        tqdm.write(f"hit error {e}")
        if isinstance(e, IndexError):
            tqdm.write("(probably you've got all activities!? nice!)")
        if isinstance(e, RequestHadError) and "Resource Not Found" in str(e):
            tqdm.write('"Resource Not Found", maybe treadmill? CONTINUING!')
            continue
        # END_ACTIVITY_IDX = idx
        break
    else:
        out_file = (
            MY_DATA_FOLDER
            / f"activity_{activity_id}.json"
        )
        out_file.write_text(json.dumps(result[activity_id]))
        print(f"saved out data to {out_file}")
