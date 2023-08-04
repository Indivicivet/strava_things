import requests
from pathlib import Path


client_id = input(
    "go to https://www.strava.com/settings/api\n"
    "client_id=? "
)
client_secret = input("client_secret=? ")
code = input(
    "now go to (and Authorize):\n"
    "https://www.strava.com/oauth/authorize"
    f"?client_id={client_id}"
    "&redirect_uri=https://localhost"
    "&response_type=code&scope=activity:read_all"
    "\n(copy from browser URL) code=? "
)

resp = requests.post(
    "https://www.strava.com/oauth/token?"
    f"client_id={client_id}&"
    f"client_secret={client_secret}&"
    f"code={code}&"
    "grant_type=authorization_code"
).json()
print(resp)
print()
print("access token:", resp["access_token"])
print("refresh token:", resp["refresh_token"])


folder = Path(__file__).parent / "secrets"
folder.mkdir(exist_ok=True, parents=True)
for tok in ["access", "refresh"]:
    (folder / f"latest_{tok}.txt").write_text(resp[f"{tok}_token"])
