import datetime
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import strava_shared

INCLUDE_WALKS = False

runs = strava_shared.load_runs(require_cadences=False)

# Filter for runs (and walks if INCLUDE_WALKS is True)
filtered_runs = []
for run in runs:
    if run.activity_type == "Run":
        filtered_runs.append(run)
    elif INCLUDE_WALKS and run.activity_type == "Walk":
        filtered_runs.append(run)

yearly_non_dec_volume = defaultdict(float)
yearly_dec_volume = defaultdict(float)
yearly_daily_volumes = defaultdict(lambda: defaultdict(float))

for run in filtered_runs:
    year = run.date.year
    month = run.date.month
    day_of_year = run.date.timetuple().tm_yday
    distance_km = run.distance[-1] / 1000.0
    if month == 12:
        yearly_dec_volume[year] += distance_km
    else:
        yearly_non_dec_volume[year] += distance_km
    yearly_daily_volumes[year][day_of_year] += distance_km

years = sorted(yearly_daily_volumes.keys())

sns.set()
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(2, 2)

# top: not-dec vs dec
ax1 = fig.add_subplot(gs[0, 0])
non_dec_vals = [yearly_non_dec_volume[y] for y in years]
ax1.bar(years, non_dec_vals, color="steelblue")
ax1.set_title("Total Run Volume: Jan - Nov")
ax1.set_ylabel("Distance (km)")
ax1.set_xticks(years)

ax2 = fig.add_subplot(gs[0, 1])
dec_vals = [yearly_dec_volume[y] for y in years]
ax2.bar(years, dec_vals, color="darkorange")
ax2.set_title("Total Run Volume: December")
ax2.set_ylabel("Distance (km)")
ax2.set_xticks(years)

# Bottom: KDE of daily volume
ax3 = fig.add_subplot(gs[1, :])
for year in years:
    days = []
    weights = []
    for day, volume in yearly_daily_volumes[year].items():
        days.append(day)
        weights.append(volume)
    sns.kdeplot(
        x=days,
        weights=weights,
        label=str(year),
        ax=ax3,
        bw_adjust=0.5,
        clip=(1, 366),
    )

ax3.set_title("Running Volume")
ax3.set_xlabel("Day")
ax3.set_ylabel("Volume (km)")
ax3.set_xlim(1, 366)
ax3.legend(title="Year")

plt.tight_layout()
plt.show()
