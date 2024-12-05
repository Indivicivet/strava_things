from pathlib import Path

import requests


secrets_folder = Path(__file__).parent / "secrets"
secrets_folder.mkdir(exist_ok=True, parents=True)
client_id_file = secrets_folder / "client_id_and_secret.txt"
if client_id_file.exists():
    print(f"using client_id and client_secret from {client_id_file}")
    client_id, client_secret = client_id_file.read_text().strip().splitlines()
else:
    client_id = input(
        "go to https://www.strava.com/settings/api"
        " to get client id and secret\n"
        "client_id=? "
    )
    client_secret = input("client_secret=? ")
    client_id_file.write_text(f"{client_id}\n{client_secret}")
    print(f"wrote client id and client secret to {client_id_file}")


code = input(
    "now go to (and Authorize):\n"
    "https://www.strava.com/oauth/authorize"
    f"?client_id={client_id}"
    "&redirect_uri=https://localhost"
    "&response_type=code&scope=activity:read_all"
    "\n(copy from browser URL) code=? "
)
if "code=" in code:  # full URL was copy-pasted
    code = code[code.index("code=") + 5:].split("&")[0]

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


secrets_folder.mkdir(exist_ok=True, parents=True)
for tok in ["access", "refresh"]:
    out_file = secrets_folder / f"latest_{tok}.txt"
    out_file.write_text(resp[f"{tok}_token"])
    print(f"wrote to {out_file}")
