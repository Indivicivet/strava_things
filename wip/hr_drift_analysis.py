"""
WIP vibe coded HR drift analysis haven't actually figured out properly
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import seaborn

import strava_shared


# Constants for HM Prediction
# Estimated Half Marathon average heart rate is around 88% of max HR for most runners.
HM_INTENSITY_FACTOR = 0.88
HM_DISTANCE_KM = 21.0975


def calculate_ef(speed_m_min, hr):
    """Efficiency Factor = Speed (m/min) / Heart Rate"""
    return speed_m_min / hr if hr > 0 else 0


def find_stability_point(times, hr, min_wait_s=600, window_s=120, slope_threshold=0.01):
    """
    Finds the index where HR stabilizes.
    Skips min_wait_s, then looks for a window where the HR slope is below threshold.
    """
    start_idx = 0
    while start_idx < len(times) and times[start_idx] < min_wait_s:
        start_idx += 1

    if start_idx >= len(times) - 1:
        return start_idx

    # Simple sliding window stability check
    for i in range(start_idx, len(times)):
        current_time = times[i]
        # Find points in window [current_time, current_time + window_s]
        window_indices = [
            j for j in range(i, len(times)) if times[j] <= current_time + window_s
        ]
        if len(window_indices) < 5:
            continue

        window_hr = [hr[j] for j in window_indices]
        window_times = [times[j] for j in window_indices]

        # Calculate slope
        slope, _, _, _, _ = stats.linregress(window_times, window_hr)
        if abs(slope) < slope_threshold:
            return i

    return start_idx


def analyze_activity(activity):
    if not activity.heartrate or not activity.velocity or not activity.time:
        return None

    # We need a decent length for drift analysis
    total_time_s = (
        activity.time[-1] - activity.time[0]
        if isinstance(activity.time[0], (int, float))
        else (activity.time[-1] - activity.time[0]).total_seconds()
    )

    if total_time_s < 1800:  # 30 mins
        return None

    times = []
    start_t = activity.time[0]
    for t in activity.time:
        if isinstance(t, (int, float)):
            times.append(t - start_t)
        else:
            times.append((t - start_t).total_seconds())

    hr = activity.heartrate
    # velocity is in m/s, convert to m/min for EF
    speed_m_min = [v * 60 for v in activity.velocity]

    stability_idx = find_stability_point(times, hr)

    stable_times = times[stability_idx:]
    stable_speed = speed_m_min[stability_idx:]
    stable_hr = hr[stability_idx:]

    if len(stable_times) < 100:
        return None

    efficiency_ratios = [calculate_ef(s, h) for s, h in zip(stable_speed, stable_hr)]

    # Linear regression on Efficiency vs Time
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        stable_times, efficiency_ratios
    )

    avg_ef = np.mean(efficiency_ratios)

    # Drift calculation: How much did EF drop from intercept to end of activity?
    start_ef_fitted = intercept + slope * stable_times[0]
    end_ef_fitted = intercept + slope * stable_times[-1]
    total_drift_pct = (
        (start_ef_fitted - end_ef_fitted) / start_ef_fitted * 100
        if start_ef_fitted > 0
        else 0
    )

    return {
        "date": activity.date,
        "avg_ef": avg_ef,
        "slope": slope,
        "drift_pct": total_drift_pct,
        "max_hr": max(hr),
        "duration_min": total_time_s / 60,
        "distance_km": activity.distance[-1] / 1000.0,
    }


def main():
    seaborn.set()
    activities = strava_shared.load_activities(require_cadences=False)
    results = []

    for act in activities:
        res = analyze_activity(act)
        if res:
            results.append(res)

    if not results:
        print("No suitable activities found for HR drift analysis.")
        return

    # Sort by date
    results.sort(key=lambda x: x["date"])

    # HM Prediction logic
    # Use recent max HR as a proxy for fitness level
    # In a real app we'd ask the user, but we can guess from their hardest efforts
    global_max_hr = max(res["max_hr"] for res in results)
    hm_target_hr = global_max_hr * HM_INTENSITY_FACTOR

    # Calculate rolling predictions over time
    for i in range(len(results)):
        # Calculate rolling metrics based on the preceding 5 runs (inclusive of current)
        window = results[max(0, i - 4) : i + 1]
        rolling_ef = np.median([r["avg_ef"] for r in window])
        rolling_drift_per_min = np.mean(
            [r["drift_pct"] / r["duration_min"] for r in window]
        )

        # Predicted Pace (m/min) = EF * TargetHR
        pred_pace_m_min = rolling_ef * hm_target_hr
        # Fatigue Penalty (based on 90 min race, so 45 min midpoint)
        dur_penalty = 1.0 - (rolling_drift_per_min * 45 / 100)
        adj_pace_m_min = pred_pace_m_min * dur_penalty

        # Total Predicted HM Time in minutes
        results[i]["predicted_hm_min"] = HM_DISTANCE_KM * 1000 / adj_pace_m_min

    # Use the final calculation for the printed summary
    final_hm_min = results[-1]["predicted_hm_min"]
    final_pace_m_min = (HM_DISTANCE_KM * 1000) / final_hm_min
    pace_min_km = 1000 / final_pace_m_min
    pace_min = int(pace_min_km)
    pace_sec = int((pace_min_km - pace_min) * 60)

    print(f"\n--- HR Drift & Efficiency Analysis ---")
    print(f"Global Max HR detected: {global_max_hr} bpm")
    print(
        f"Assumed HM Intensity: {hm_target_hr:.1f} bpm ({HM_INTENSITY_FACTOR*100}% of Max)"
    )
    print(f"Current Baseline EF: {results[-1]['avg_ef']:.3f}")
    print(
        f"Current Drift Rate: {(results[-1]['drift_pct'] / results[-1]['duration_min']):.3f}% per minute"
    )

    print(f"\n--- Half Marathon Prediction (Latest) ---")
    print(f"Predicted Pace: {pace_min}:{pace_sec:02d} /km")
    print(
        f"Predicted Time: {int(final_hm_min//60)}h {int(final_hm_min%60)}m {int((final_hm_min*60)%60)}s"
    )

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 14), sharex=True)

    dates = [r["date"] for r in results]
    efs = [r["avg_ef"] for r in results]
    drifts = [r["drift_pct"] for r in results]
    hm_times = [r["predicted_hm_min"] for r in results]

    ax1.plot(dates, efs, "o-", label="Efficiency Factor (Speed/HR)")
    ax1.set_title("Aerobic Efficiency Over Time")
    ax1.set_ylabel("EF (Lower is less efficient)")

    ax2.plot(dates, drifts, "o-", alpha=0.7, label="Drift %")
    ax2.set_title("Heart Rate Drift % (Stable Portion)")
    ax2.set_ylabel("Drift %")
    ax2.axhline(5, color="#444444", linestyle="--", label="5% Threshold")

    ax3.plot(dates, hm_times, "o-", label="Predicted HM Time")
    ax3.set_title("Predicted Half Marathon Time Over Time (Rolling 5-Run Window)")
    ax3.set_ylabel("Time (minutes)")
    ax3.set_xlabel("Date")

    plt.tight_layout()
    plt.savefig("hr_drift_trends.png")
    print("\nTrends plot saved to hr_drift_trends.png")
    plt.show()


if __name__ == "__main__":
    main()
