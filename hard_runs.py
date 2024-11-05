"""
old script - todo :: update to use strava shared ^^
"""


import requests
import time
from pathlib import Path

#resp = requests.post(
#    "https://www.strava.com/oauth/token?"
#    "client_id=CLIENT_ID&"
#    "client_secret=CLIENT_SECRET&"
#    "code=CODE_FROM_THING&"
#    "grant_type=authorization_code"
#)
#print(resp.json())

token = (
    Path(__file__).parents[1] / "access_tokens_2023" / "strava_token.txt"
).read_text().strip()

def get_activity(id=9535755237):
    return requests.get(
        f"https://www.strava.com/api/v3/activities/{id}"
        f"?include_all_efforts=",
        headers={"Authorization": "Bearer " + token}
    )

def get_activities(per_page=30):
    return requests.get(
        f"https://www.strava.com/api/v3/athlete/activities?before="
        f"{int(time.time())}&after=964796319&per_page={per_page}",
        headers={"Authorization": "Bearer " + token},
    ).json()

ra = get_activities(80)

for l in [
    (r["start_date"], r["average_speed"] / r["average_heartrate"])
    for r in ra
    if r["has_heartrate"]
       and r["distance"] > 5000
       and r["max_heartrate"] > 150
]:
    print(l[0].replace("T", " ").replace("Z", ""), ",", l[1])
