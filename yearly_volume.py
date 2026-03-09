import datetime
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import strava_shared

RUNS_ONLY = True

runs = strava_shared.load_runs(require_cadences=False)

filtered_runs = [
    run for run in runs if run.activity_type == "Run" or not RUNS_ONLY
]

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

# Smoothing kernel


def get_daily_array(y):
    arr = np.zeros(366)
    for d, vol in yearly_daily_volumes[y].items():
        if 1 <= d <= 366:
            arr[d - 1] = vol
    return arr


SIGMA = 7
PAD = 3 * SIGMA
x_kernel = np.arange(-PAD, PAD + 1)
kernel = np.exp(-(x_kernel**2) / (2 * SIGMA**2))
kernel /= kernel.sum()

for year in years:
    # pad each year with adjacent years if possible
    padded_vol = np.concatenate([
        (
            get_daily_array(year - 1)[-PAD:]
            if year - 1 in yearly_daily_volumes
            else np.zeros(PAD)
        ),
        get_daily_array(year),
        (
            get_daily_array(year + 1)[:PAD]
            if year + 1 in yearly_daily_volumes
            else np.zeros(PAD)
        ),
    ])
    ax3.plot(
        np.arange(1, 367),
        np.convolve(padded_vol, kernel, mode="valid"),
        label=str(year),
    )

ax3.set_title("Running Volume")
ax3.set_xlabel("Day")
ax3.set_ylabel("Volume (km)")
ax3.set_xlim(1, 366)
ax3.set_ylim(bottom=0)
ax3.legend(title="Year")

plt.tight_layout()
plt.show()
