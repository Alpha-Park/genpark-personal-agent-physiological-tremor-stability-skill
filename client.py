"""
Physiological Tremor & Neuromuscular Steadiness Engine.
Provides deterministic, zero-dependency spectral analysis of physiological microtremor,
evaluating neuromuscular fatigue, 8-12 Hz central motor oscillations, and postural stability.
"""

import math
from typing import Dict, Any, List, Optional


class PhysiologicalTremorClient:
    """
    Deterministic client for analyzing physiological tremor waveforms and neuromuscular steadiness.
    Pure Python standard library implementation based on discrete spectral decomposition.
    """

    def __init__(self):
        pass

    def _compute_dft_power_spectrum(self, samples: List[float], sample_rate: float) -> tuple[List[float], List[float]]:
        """
        Compute discrete Fourier transform power spectrum for detrended signal.
        Returns frequencies and power spectral densities.
        """
        n = len(samples)
        if n == 0:
            return [], []

        mean_val = sum(samples) / n
        detrended = [s - mean_val for s in samples]

        # Use up to 256 points for efficiency while preserving high frequency resolution
        step = max(1, n // 256)
        sub_samples = detrended[::step]
        n_sub = len(sub_samples)
        eff_rate = sample_rate / step

        freqs = []
        powers = []
        num_freqs = n_sub // 2

        for k in range(1, num_freqs):
            freq = (k * eff_rate) / n_sub
            if freq > 30.0:  # Bound to physiological tremor interest zone (< 30 Hz)
                break
            re = 0.0
            im = 0.0
            for t in range(n_sub):
                angle = 2.0 * math.pi * k * t / n_sub
                re += sub_samples[t] * math.cos(angle)
                im -= sub_samples[t] * math.sin(angle)
            power = (re * re + im * im) / (n_sub * n_sub)
            freqs.append(round(freq, 2))
            powers.append(power)

        return freqs, powers

    def analyze_tremor_timeseries(
        self,
        acceleration_samples: List[float],
        sample_rate_hz: float = 50.0,
        axis_name: str = "dominant_axis"
    ) -> Dict[str, Any]:
        """
        Analyze accelerometer/gyroscope tremor series in m/s² or milli-g.
        Extracts dominant frequency, 8-12 Hz physiological band ratio, RMS amplitude, and fatigue index.
        """
        if not acceleration_samples:
            return {"error": "Empty acceleration samples provided"}

        n = len(acceleration_samples)
        mean_val = sum(acceleration_samples) / n
        variance = sum((x - mean_val) ** 2 for x in acceleration_samples) / n
        rms_amplitude = math.sqrt(variance)

        freqs, powers = self._compute_dft_power_spectrum(acceleration_samples, sample_rate_hz)

        if not powers or sum(powers) == 0.0:
            total_power = 0.0
            p_low = 0.0
            p_physio = 0.0
            p_high = 0.0
            peak_freq = 0.0
        else:
            total_power = sum(powers)
            p_low = sum(p for f, p in zip(freqs, powers) if 3.0 <= f < 7.0)
            p_physio = sum(p for f, p in zip(freqs, powers) if 7.0 <= f <= 12.0)
            p_high = sum(p for f, p in zip(freqs, powers) if 12.0 < f <= 25.0)

            max_idx = powers.index(max(powers))
            peak_freq = freqs[max_idx]

        ratio_physio = round(p_physio / total_power, 4) if total_power > 0 else 0.0
        ratio_low = round(p_low / total_power, 4) if total_power > 0 else 0.0
        ratio_high = round(p_high / total_power, 4) if total_power > 0 else 0.0

        # Postural Tremor Stability Index (0 - 100)
        # Scaled where low RMS (< 0.15 m/s²) and dominant 8-12 Hz band represents ideal steadiness
        rms_penalty = min(50.0, (rms_amplitude / 0.5) * 50.0)
        low_freq_penalty = min(30.0, ratio_low * 30.0)
        stability_score = max(5.0, min(100.0, 100.0 - rms_penalty - low_freq_penalty + (ratio_physio * 20.0)))

        # Fatigue state detection: peak frequency shift < 8.2 Hz with elevated amplitude
        is_motor_fatigued = (peak_freq < 8.2 and peak_freq >= 6.0 and rms_amplitude > 0.20)
        is_sympathetic_aroused = (peak_freq >= 10.5 and rms_amplitude > 0.25)

        if stability_score >= 80.0:
            status = "OPTIMAL_MOTOR_STEADINESS"
            guidance = "Excellent neuromuscular stability. Baseline tone is calm with standard physiological microtremor."
        elif stability_score >= 60.0:
            status = "MILD_POSTURAL_AROUSAL"
            guidance = "Slightly elevated tremor amplitude; consistent with routine sympathetic activation or minor caffeine load."
        elif is_motor_fatigued:
            status = "CENTRAL_MOTOR_FATIGUE"
            guidance = "Low-frequency power shift detected (< 8.2 Hz). Neuromuscular fatigue present; schedule 15-minute ergonomic rest."
        else:
            status = "ELEVATED_TREMOR_EXCESS"
            guidance = "Pronounced tremor oscillations detected. Recommend hydration check, caffeine halflife clearance, and somatic relaxation."

        return {
            "axis": axis_name,
            "sample_count": n,
            "sample_rate_hz": sample_rate_hz,
            "rms_amplitude": round(rms_amplitude, 4),
            "dominant_peak_frequency_hz": peak_freq,
            "physiological_band_power_ratio": ratio_physio,
            "low_frequency_power_ratio": ratio_low,
            "high_frequency_power_ratio": ratio_high,
            "tremor_stability_index": round(stability_score, 1),
            "is_motor_fatigued": is_motor_fatigued,
            "is_sympathetic_aroused": is_sympathetic_aroused,
            "status": status,
            "guidance": guidance
        }

    def assess_postural_vs_rest_ratio(
        self,
        rest_samples: List[float],
        postural_samples: List[float],
        sample_rate_hz: float = 50.0
    ) -> Dict[str, Any]:
        """
        Evaluate Rest vs Postural Tremor Ratio.
        Normal physiological tremor is postural (present against gravity) and negligible at complete rest.
        """
        rest_res = self.analyze_tremor_timeseries(rest_samples, sample_rate_hz, "rest_state")
        post_res = self.analyze_tremor_timeseries(postural_samples, sample_rate_hz, "postural_state")

        rest_rms = rest_res.get("rms_amplitude", 0.0)
        post_rms = post_res.get("rms_amplitude", 0.001)

        ratio = round(rest_rms / max(0.0001, post_rms), 3)

        # In physiological tremor, postural RMS is significantly greater than resting RMS (ratio << 1.0)
        is_normal_physio = ratio < 0.60

        return {
            "rest_rms_amplitude": rest_rms,
            "postural_rms_amplitude": post_rms,
            "rest_to_postural_ratio": ratio,
            "is_physiologically_normal": is_normal_physio,
            "postural_stability_index": post_res.get("tremor_stability_index"),
            "interpretation": (
                "Normal physiological microtremor pattern: tremor amplitude sharply attenuates at rest."
                if is_normal_physio else
                "Elevated resting tremor ratio detected; review motor relaxation and assess for peripheral neuromuscular tension."
            )
        }
