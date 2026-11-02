---
name: genpark-personal-agent-physiological-tremor-stability-skill
description: Real-time deterministic spectral analysis of physiological microtremor waveforms, 8-12 Hz central oscillator power, and neuromuscular fatigue monitoring.
version: 1.0.0
author: GenPark Autonomous Agents Ecosystem
license: MIT
tags:
  - personal-agent
  - ai-agent
  - openclaw
  - genpark
  - mcp
  - mcp-server
  - model-context-protocol
  - python
  - zero-dependency
  - wellness
  - productivity
  - production-ready
---

# Physiological Tremor & Neuromuscular Steadiness Skill

## Overview
The `genpark-personal-agent-physiological-tremor-stability-skill` empowers personal sovereign agents with deterministic spectral processing of physiological microtremor oscillations. Physiological tremor occurs naturally in the 8-12 Hz frequency band due to central mechanical resonance and spinocerebellar reflex loops. This skill quantifies central motor drive exhaustion, evaluates resting vs postural tremor ratios, and alerts when sympathetic arousal or motor fatigue degrades manual dexterity.

## Physiological Model & Mathematics
1. **Discrete Fourier Spectral Density**:
   $$\text{Power}(f_k) = \frac{1}{N^2} \left[ \left(\sum x_t \cos \frac{2\pi k t}{N}\right)^2 + \left(\sum x_t \sin \frac{2\pi k t}{N}\right)^2 \right]$$
2. **Physiological Band Ratio ($RPTR$)**:
   $$RPTR = \frac{P_{8-12\text{Hz}}}{P_{\text{total}}}$$
3. **Root Mean Square (RMS) Tremor Amplitude**:
   $$A_{\text{rms}} = \sqrt{\frac{1}{N}\sum_{t=1}^N (x_t - \bar{x})^2}$$
4. **Postural Tremor Stability Index ($PTSI$)**:
   Evaluates neuromuscular stability from 0 to 100 based on low RMS acceleration penalty, absence of low-frequency (< 7 Hz) pathological surge, and sharp 8-12 Hz resonance.

## Tools & Endpoints
- `analyze_tremor_timeseries`: Spectral power decomposition, dominant frequency determination, and motor fatigue categorization.
- `assess_postural_vs_rest_ratio`: Compares rest vs postural state RMS to verify benign physiological microtremor status.
