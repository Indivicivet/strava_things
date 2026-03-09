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
sigma = 7  # Days for smoothing
pad = 3 * sigma
x_kernel = np.arange(-pad, pad + 1)
kernel = np.exp(-(x_kernel**2) / (2 * sigma**2))
kernel /= kernel.sum()


def get_daily_array(y):
    arr = np.zeros(366)
    for d, vol in yearly_daily_volumes[y].items():
        if 1 <= d <= 366:
            arr[d - 1] = vol
    return arr


for year in years:
    daily_vol = get_daily_array(year)

    # Pad with adjacent years if possible, otherwise repeat current year edges
    if year - 1 in yearly_daily_volumes:
        prev_tail = get_daily_array(year - 1)[-pad:]
    else:
        prev_tail = daily_vol[
            :pad
        ]  # fallback: repeat start (mirroring or just repeating)
        # Actually, user said "preceding year's values".
        # If no preceding year, we might just have to accept 0 or repeat.
        # Let's repeat the first day's value or similar to avoid the drop.
        prev_tail = np.full(pad, daily_vol[0])

    if year + 1 in yearly_daily_volumes:
        next_head = get_daily_array(year + 1)[:pad]
    else:
        next_head = np.full(pad, daily_vol[-1])

    padded_vol = np.concatenate([prev_tail, daily_vol, next_head])

    # Smooth using 'valid' to get exactly 366 days back
    smoothed_vol = np.convolve(padded_vol, kernel, mode="valid")

    ax3.plot(
        np.arange(1, 367),
        smoothed_vol,
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
