import numpy as np
import pyproj
import seaborn
from matplotlib import pyplot as plt

import strava_shared

# LENGTH_WEIGHTING = 1.5  # used as an exponent in places_ive_been.py, skip here?

TAKE_EVERY_N_PTS = 10
MAX_LATLNG_FROM_CENTER = 10
MAX_LATLNG_SQUARED = MAX_LATLNG_FROM_CENTER ** 2

runs = [
    run for run in strava_shared.load_runs(require_cadences=False) if run.latlng
]
# this is quick
run_mean_latlngs = [np.mean(run.latlng, axis=0) for run in runs]
mean_latlng = np.mean(run_mean_latlngs, axis=0)
if MAX_LATLNG_FROM_CENTER is not None:
    unfiltered_n = len(runs)
    runs = [
        run
        for run, center in zip(runs, run_mean_latlngs)
        if ((center - mean_latlng) ** 2).sum() < MAX_LATLNG_SQUARED
    ]
    print(
        f"using {len(runs)} / {unfiltered_n} runs"
        f" (based on max latlng distance {MAX_LATLNG_FROM_CENTER})"
    )
    run_mean_latlngs = [np.mean(run.latlng, axis=0) for run in runs]
    mean_latlng = np.mean(run_mean_latlngs, axis=0)


lat0, lng0 = mean_latlng
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

print(len(all_x))

print("plotting")  # this is slow
seaborn.kdeplot(
    x=all_x,
    y=all_y,
    levels=15,
    fill=True,
)
plt.show()
