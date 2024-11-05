import datetime
import time
from pathlib import Path

import matplotlib.dates as plt_dates
import matplotlib.pyplot as plt
import seaborn


DISTANCES = {
    "1k": 1,
    "1 mile": 1.60934,
    "5k": 5,
    "10k": 10,
    "half": 21.0975,
    "marathon": 42.195,
}


def time_to_secs(time_str):
    parts = [int(x) for x in time_str.split(":")]
    minsec = parts[-1] + parts[-2] * 60
    if len(parts) == 2:
        return minsec
    return minsec + parts[-3] * 60 * 60


def to_paces(times_str):
    times = [time_to_secs(s) for s in times_str.split(",")]
    paces = [int(t / d) for t, d in zip(times, DISTANCES.values())]
    paces += [8 * 60] * (len(DISTANCES) - len(paces))
    return [
        datetime.datetime.strptime(
            time.strftime("%M:%S", time.gmtime(pace)),
            "%M:%S",
        )
        for pace in paces
    ]


all_paces = {
    name: to_paces(times_str=times_str)
    for line in (
        Path(__file__).parent / "my_data" / "runners_times.txt"
    ).read_text().splitlines()
    for (name, times_str) in [line.split(" = ")]
}


seaborn.set()

fig, ax = plt.subplots()
for person, paces in all_paces.items():
    ax.plot(list(DISTANCES.keys()), paces)

ax.yaxis.set_major_formatter(plt_dates.DateFormatter("%M:%S"))
plt.xlabel("distance")
plt.ylabel("pace (MM:SS / km)")
plt.gca().invert_yaxis()
plt.legend(all_paces.keys())
plt.show()
