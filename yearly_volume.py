import datetime
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import strava_shared

RUNS_ONLY_FOR_KDE = True

runs = strava_shared.load_runs(require_cadences=False)

yearly_run_non_dec_volume = defaultdict(float)
yearly_run_dec_volume = defaultdict(float)
yearly_other_non_dec_volume = defaultdict(float)
yearly_other_dec_volume = defaultdict(float)
yearly_daily_volumes = defaultdict(lambda: defaultdict(float))

for run in runs:
    is_run = run.activity_type == "Run"
    year = run.date.year
    month = run.date.month
    day_of_year = run.date.timetuple().tm_yday
    distance_km = run.distance[-1] / 1000.0

    if is_run:
        if month == 12:
            yearly_run_dec_volume[year] += distance_km
        else:
            yearly_run_non_dec_volume[year] += distance_km
    else:
        if month == 12:
            yearly_other_dec_volume[year] += distance_km
        else:
            yearly_other_non_dec_volume[year] += distance_km

    if is_run or not RUNS_ONLY_FOR_KDE:
        yearly_daily_volumes[year][day_of_year] += distance_km

years = sorted(yearly_daily_volumes.keys())

sns.set()
fig = plt.figure(figsize=(14, 10))
gs = fig.add_gridspec(2, 2)

# top: not-dec vs dec
ax1 = fig.add_subplot(gs[0, 0])
non_dec_run_vals = [yearly_run_non_dec_volume[y] for y in years]
non_dec_other_vals = [yearly_other_non_dec_volume[y] for y in years]
ax1.bar(years, non_dec_run_vals, color="steelblue", label="Runs")
ax1.bar(
    years,
    non_dec_other_vals,
    bottom=non_dec_run_vals,
    color="steelblue",
    alpha=0.3,
    label="Other",
)
ax1.set_title("Total Volume: Jan - Nov")
ax1.set_ylabel("Distance (km)")
ax1.set_xticks(years)
ax1.legend()

ax2 = fig.add_subplot(gs[0, 1])
dec_run_vals = [yearly_run_dec_volume[y] for y in years]
dec_other_vals = [yearly_other_dec_volume[y] for y in years]
ax2.bar(years, dec_run_vals, color="darkorange", label="Runs")
ax2.bar(
    years,
    dec_other_vals,
    bottom=dec_run_vals,
    color="darkorange",
    alpha=0.3,
    label="Other",
)
ax2.set_title("Total Volume: December")
ax2.set_ylabel("Distance (km)")
ax2.set_xticks(years)
ax2.legend()

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
    padded_vol = np.concatenate(
        [
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
        ]
    )
    ax3.plot(
        np.arange(1, 367),
        np.convolve(padded_vol, kernel, mode="valid"),
        label=str(year),
    )

ax3.set_title("Running Volume" if RUNS_ONLY_FOR_KDE else "Total Volume")
ax3.set_xlabel("Day")
ax3.set_ylabel("Volume (km)")
ax3.set_xlim(1, 366)
ax3.set_ylim(bottom=0)
ax3.legend(title="Year")

plt.tight_layout()
plt.show()
