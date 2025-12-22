import numpy as np
import pyproj
from matplotlib import pyplot as plt
import matplotlib
from scipy import ndimage

import strava_shared

# LENGTH_WEIGHTING = 1.5  # used as an exponent in places_ive_been.py, skip here?

WEIGHT_CENTERED = 0.5
BINS = 2000

TAKE_EVERY_N_PTS = 1  # increase if too many datapoints :) 1 should be ok tho
MAX_LATLNG_FROM_CENTER = 2
MAX_LATLNG_SQUARED = MAX_LATLNG_FROM_CENTER ** 2

runs = [
    run for run in strava_shared.load_runs(require_cadences=False) if run.latlng
]
print(runs[0].latlng[0])
# this is quick
run_mean_latlngs = [np.mean(run.latlng, axis=0) for run in runs]
median_latlng = np.median(run_mean_latlngs, axis=0)
if MAX_LATLNG_FROM_CENTER is not None:
    unfiltered_n = len(runs)
    runs = [
        run
        for run, center in zip(runs, run_mean_latlngs)
        if ((center - median_latlng) ** 2).sum() < MAX_LATLNG_SQUARED
    ]
    print(
        f"using {len(runs)} / {unfiltered_n} runs"
        f" (based on max latlng distance {MAX_LATLNG_FROM_CENTER})"
    )
    run_mean_latlngs = [np.mean(run.latlng, axis=0) for run in runs]
    median_latlng = np.median(run_mean_latlngs, axis=0)


lat0, lng0 = median_latlng
transformer = pyproj.Transformer.from_crs(
    pyproj.CRS.from_epsg(4326),  # wgs84
    pyproj.CRS.from_proj4(
        # azimuthal equidistant
        "+proj=aeqd"
        f" +lat_0={lat0} +lon_0={lng0}"
        " +datum=WGS84 +units=m +no_defs"
    ),
    always_xy=True,
)


def get_km(latlng):
    x_m, y_m = transformer.transform(latlng[1], latlng[0])
    return x_m / 1000, y_m / 1000


all_x, all_y = np.array([
    get_km(latlng) for run in runs for latlng in run.latlng[::TAKE_EVERY_N_PTS]
]).T

# print(len(all_x))

weights = None
if WEIGHT_CENTERED is not None:
    counts, x_edges, y_edges = np.histogram2d(all_x, all_y, bins=BINS)
    i, j = np.unravel_index(np.argmax(counts), counts.shape)
    x0 = 0.5 * (x_edges[i] + x_edges[i + 1])
    y0 = 0.5 * (y_edges[j] + y_edges[j + 1])
    # weight based on distance:
    weights = ((all_x - x0) ** 2 + (all_y - y0) ** 2) ** (WEIGHT_CENTERED / 2)

histogram_arr, x_edges, y_edges = np.histogram2d(
    all_x,
    all_y,
    bins=BINS,
    weights=weights,
)
fig, ax = plt.subplots(figsize=(9, 9))
ax.set_facecolor("black")
plt.imshow(
    ndimage.gaussian_filter(histogram_arr, sigma=2).T,
    origin="lower",
    extent=(x_edges[0], x_edges[-1], y_edges[0], y_edges[-1]),
    norm=matplotlib.colors.LogNorm(vmin=0.05),
    cmap="inferno",
    interpolation="nearest",
)
ax.margins(0)
fig.tight_layout(pad=0)
plt.gca().set_aspect("equal", "box")
plt.show()
