import datetime
import math
import time
from dataclasses import dataclass

import matplotlib
from matplotlib import pyplot as plt
import numpy as np
import seaborn
from tqdm import tqdm

import strava_shared


seaborn.set()
plt.style.use("dark_background")

runs = strava_shared.load_runs(require_cadences=False)

#max_distance = max(run.distance[-1] for run in runs)
PLOT_DISTANCE_INTERVAL = 100

JUST_PLOT_HRS = False

HR_MIN = 130
HR_MAX = 200

PLOT_TOPLINES_ONLY = True
TOPLINE_DATE_CUTOFFS = [
    datetime.datetime(3000, 1, 1),
    datetime.datetime(2023, 7, 1),
    datetime.datetime(2023, 1, 1),
    datetime.datetime(2022, 7, 1),
]


def hr_to_01(hr):
    return np.clip(
        (np.array(hr) - HR_MIN) / (HR_MAX - HR_MIN),
        0, 1
    )


color_map_from_01 = matplotlib.cm.get_cmap("RdYlBu").reversed()


def color_map(hr):
    return color_map_from_01(hr_to_01(hr))


START_DISTANCE_IDX = 2


@dataclass
class IntervalStatistics:
    times: np.ndarray
    hrs: np.ndarray
    interval_length: int = PLOT_DISTANCE_INTERVAL  # todo :: could be float...?
    start_idx: int = START_DISTANCE_IDX

    def __post_init__(self):
        assert len(self.times) == len(self.hrs), (
            f"{len(self.times)=} != {len(self.hrs)=}"
        )

    @property
    def intervals(self):
        return (
            self.start_idx + np.arange(len(self.times))
        ) * self.interval_length

    def get_pace_datetimes(self):
        return [
            datetime.datetime.fromtimestamp(t * 1000 / interval)
            for interval, t in zip(self.intervals, self.times)
        ]

    @classmethod
    def for_length_by_defaults(cls, run_length):
        # todo :: this using cls.defaults is probably bad??
        n_length = math.ceil(run_length / cls.interval_length) - cls.start_idx
        return cls(
            times=np.full(n_length, fill_value=9999),
            hrs=np.full(n_length, fill_value=100),
        )

    def update_with(self, other_stats):  # intervalstatistics^2->intervalstats
        # todo :: maybe not the nicest...
        result = type(self)(
            times=self.times,
            hrs=self.hrs,
            interval_length=self.interval_length,
            start_idx=self.start_idx,
        )
        need_extend_by = len(other_stats.times) - len(result.times)
        if need_extend_by > 0:
            result.times = np.append(
                result.times,
                [99999] * need_extend_by,
            )
            result.hrs = np.append(result.hrs, [0] * need_extend_by)
        # todo :: also kinda yucky code with this np array vs list business
        other_times = np.append(
            other_stats.times, [99999] * max(-need_extend_by, 0)
        )
        other_hrs = np.append(
            other_stats.hrs, [0] * max(-need_extend_by, 0)
        )
        where_update = other_times < result.times
        result.times[where_update] = other_times[where_update]
        result.hrs[where_update] = other_hrs[where_update]
        return result


if PLOT_TOPLINES_ONLY:
    print("plotting toplines only")
    topline_stats = {
        cutoff: IntervalStatistics(times=np.array([]), hrs=np.array([]))
        for cutoff in TOPLINE_DATE_CUTOFFS
    }


for run in tqdm(runs[:999]):  # most recent
    best_stats = IntervalStatistics.for_length_by_defaults(run.distance[-1])
    for start_i, start_d in enumerate(run.distance):
        for latter_i, latter_d in enumerate(run.distance):
            if latter_i <= start_i:
                continue  # easiest way to code it up. probs not 2slow.
            interval_time = run.time[latter_i] - run.time[start_i]
            arr_idx = (
                int((latter_d - start_d) / PLOT_DISTANCE_INTERVAL)
                - START_DISTANCE_IDX
            )
            # todo :: not sure how the arr_idx == len(best_stats.times)
            # comes about; might be fine, or might be making arrs of bad length
            if arr_idx < 0 or arr_idx >= len(best_stats.times):
                continue
            if interval_time < best_stats.times[arr_idx]:
                best_stats.times[arr_idx] = interval_time
                if run.heartrate is not None:
                    best_stats.hrs[arr_idx] = sum(
                        run.heartrate[start_i:latter_i]
                    ) / (latter_i - start_i)
    if PLOT_TOPLINES_ONLY:
        for datetime_cutoff, timespan_stats in topline_stats.items():
            if run.date >= datetime_cutoff:
                continue
            topline_stats[datetime_cutoff] = timespan_stats.update_with(
                best_stats
            )
    if not PLOT_TOPLINES_ONLY:
        paces = best_stats.get_pace_datetimes()
        plt.plot(
            best_stats.hrs if JUST_PLOT_HRS else best_stats.intervals,
            paces,
            c=color_map(np.mean(best_stats.hrs, axis=0)),
        )
        plt.scatter(
            best_stats.hrs if JUST_PLOT_HRS else best_stats.intervals,
            paces,
            c=color_map(best_stats.hrs),
            s=20,
        )


if PLOT_TOPLINES_ONLY:
    for datetime_cutoff, timespan_stats in topline_stats.items():
        paces = timespan_stats.get_pace_datetimes()
        if not JUST_PLOT_HRS:
            plt.plot(
                timespan_stats.intervals,
                paces,
            )
        plt.scatter(
            timespan_stats.hrs if JUST_PLOT_HRS else timespan_stats.intervals,
            paces,
            c=color_map(timespan_stats.hrs),
            s=20,
            label=f"before {datetime_cutoff}",
        )
        plt.legend()


color_scalar_mappable = plt.cm.ScalarMappable(
    cmap=color_map_from_01,
    norm=plt.Normalize(vmin=HR_MIN, vmax=HR_MAX),
)
color_scalar_mappable.set_array([])  # Empty array since we only need the colormap
cbar = plt.colorbar(color_scalar_mappable)


#plt.xscale("log")
start, end = plt.gca().get_xlim()
if not JUST_PLOT_HRS:
    plt.gca().xaxis.set_ticks(range(0, int(end) + 1000, 1000))
plt.gca().yaxis.set_major_formatter(matplotlib.dates.DateFormatter("%M:%S"))
plt.gca().invert_yaxis()
plt.xlabel("HR" if JUST_PLOT_HRS else "distance")
plt.ylabel("pace (MM:SS / km)")
plt.show()
