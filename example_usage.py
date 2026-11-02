"""
Example usage for Physiological Tremor & Neuromuscular Steadiness Skill.
Demonstrates analyzing synthetic accelerometer stream and evaluating rest vs postural tremor ratio.
"""

import math
from client import PhysiologicalTremorClient


def generate_synthetic_tremor(duration_sec: float = 4.0, sample_rate: float = 50.0, freq: float = 9.5, amp: float = 0.12, noise: float = 0.03):
    samples = []
    total_pts = int(duration_sec * sample_rate)
    for i in range(total_pts):
        t = i / sample_rate
        val = amp * math.sin(2.0 * math.pi * freq * t) + noise * math.sin(2.0 * math.pi * 23.0 * t)
        samples.append(val)
    return samples


def main():
    client = PhysiologicalTremorClient()
    print("=== 1. Analyzing Postural Tremor Acceleration Series ===")
    postural_series = generate_synthetic_tremor(duration_sec=4.0, sample_rate=50.0, freq=9.5, amp=0.14)
    res_postural = client.analyze_tremor_timeseries(postural_series, sample_rate_hz=50.0, axis_name="z_vertical")
    print(f"Dominant Frequency: {res_postural['dominant_peak_frequency_hz']} Hz")
    print(f"Physiological Band Power Ratio: {res_postural['physiological_band_power_ratio']}")
    print(f"Tremor Stability Index: {res_postural['tremor_stability_index']} / 100")
    print(f"Status: {res_postural['status']}")
    print(f"Guidance: {res_postural['guidance']}")

    print("\n=== 2. Evaluating Rest vs Postural Tremor Ratio ===")
    rest_series = generate_synthetic_tremor(duration_sec=4.0, sample_rate=50.0, freq=9.0, amp=0.02)
    ratio_res = client.assess_postural_vs_rest_ratio(rest_series, postural_series, sample_rate_hz=50.0)
    print(f"Rest RMS: {ratio_res['rest_rms_amplitude']} | Postural RMS: {ratio_res['postural_rms_amplitude']}")
    print(f"Rest-to-Postural Ratio: {ratio_res['rest_to_postural_ratio']}")
    print(f"Is Physiologically Normal: {ratio_res['is_physiologically_normal']}")
    print(f"Interpretation: {ratio_res['interpretation']}")


if __name__ == "__main__":
    main()
