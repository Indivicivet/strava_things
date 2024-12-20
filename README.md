# use

## retrieving runs

firstly you need to get auth creds, these only last a day or something

for this make sure you have a strava API app and run `get_access_token.py`
after clicking the displayed link and authorizing, you'll be on an unresolved
localhost page; copy that URL (localhost + state in the GET command) into
the script and press enter.

after this you can run `download_all_streams.py` which will download 90 streams
(download cap normally ~100 requests, to avoid going over)

if you want to download anything other than most recent, you can change START_ACTIVITY_IDX

## doing things

`strava_shared.py` gives a basic interface for loadnig runs; this is then used by various scripts

all other scripts should be runnable things that produce nice outputs :)

# todos:

use refresh token

remove cycles, walks, etc (and maybe architecutre for these in the future?)
