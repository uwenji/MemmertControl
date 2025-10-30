# Run Report: run_025_baseline_test

**Status:** ✅ COMPLETED  
**Date:** 30.10.2025  
**Duration:** 5 minutes  
**Type:** baseline

---

## Executive Summary

**Run Name:** baseline_test  
**Description:** undefined

**Key Findings:**
- **Data Quality:** Poor (1.25% complete)
- **Total Readings:** 4
- **PID Actions:** 5
- **Disturbances:** 0

**Temp:**
- Settling time: 0.8 minutes
- Steady-state error: ±0.05°C
- Stability (σ): 0.03°C

**Hum:**
- Settling time: 0.8 minutes
- Steady-state error: ±0.58%
- Stability (σ): 0.36%

**CO2:**
- Steady-state error: ±1000 ppm
- Stability (σ): 0 ppm

**O2:**
- Steady-state error: ±21%
- Stability (σ): 0%

---

## Test Configuration

### Targets
| Variable | Target | Unit |
|----------|--------|------|
| Temp | 30 | °C |
| Hum | 60 | % |
| CO2 | 1000 |  ppm |
| O2 | 21 | % |
| Fan | 50 | % |

### Bioreactor State
- **Empty:** Yes
- **Contents:** Ambient air
- **Approximate mass:** 0.5 kg

### PID Parameters
| Variable | Kp | Ki | Kd |
|----------|----|----|-----|
| Temp | 2 | 0.1 | 0.5 |
| Hum | 1.5 | 0.05 | 0.3 |
| CO2 | 0.5 | 0.02 | 0.1 |
| O2 | 1 | 0.05 | 0.2 |
| Fan | 1 | 0.1 | 0.05 |

---

## Timeline

| Time | Event | Category | Notes |
|------|-------|----------|-------|
| 00:00:00 | Run started | system | - |
| 00:05:16 | system | run_stop | - |
| 00:05:19 | Run ended | system | completed |

---

## Performance Metrics

### Temp

**Target:** 30°C

**Time-Domain Response:**
- Initial value: 29.9°C
- Final value: 29.99°C
- Peak time: 4.2 minutes
- Peak value: 29.99°C
- Overshoot: 0%
- Settling time (±2%): 0.8 minutes
- Settling time (±5%): 0.8 minutes

**Steady-State Performance** (last 4 minutes):
- Mean: 29.95°C
- Standard deviation: 0.03°C
- Range: 0.09°C (29.9 to 29.99)
- Steady-state error: 0.05°C (0.2%)

### Hum

**Target:** 60%

**Time-Domain Response:**
- Initial value: 60.01%
- Final value: 60.52%
- Overshoot: 0%
- Settling time (±2%): 0.8 minutes
- Settling time (±5%): 0.8 minutes

**Steady-State Performance** (last 4 minutes):
- Mean: 60.58%
- Standard deviation: 0.36%
- Range: 0.93% (60.01 to 60.94)
- Steady-state error: 0.58% (1%)

### CO2

**Target:** 1000 ppm

**Time-Domain Response:**
- Initial value: 0 ppm
- Final value: 0 ppm
- Overshoot: 0%

**Steady-State Performance** (last 4 minutes):
- Mean: 0 ppm
- Standard deviation: 0 ppm
- Range: 0 ppm (0 to 0)
- Steady-state error: 1000 ppm (100%)

### O2

**Target:** 21%

**Time-Domain Response:**
- Initial value: 0%
- Final value: 0%
- Overshoot: 0%

**Steady-State Performance** (last 4 minutes):
- Mean: 0%
- Standard deviation: 0%
- Range: 0% (0 to 0)
- Steady-state error: 21% (100%)

---

## Disturbance Analysis

No disturbances detected or analyzed.

---

## Data Quality

**Completeness:** 1.25% (Poor)
- Expected readings: 319
- Actual readings: 4
- Missed readings: 315

**Sensor Status:**
All sensors operational

---

## Conclusions and Recommendations

### Performance Assessment

**Temp:**
- ✅ Good settling time (0.8 min)
- ✅ Minimal overshoot (0%)
- ✅ Excellent steady-state accuracy (±0.2%)
- ✅ Excellent stability (σ=0.03)

**Hum:**
- ✅ Good settling time (0.8 min)
- ✅ Minimal overshoot (0%)
- ✅ Excellent steady-state accuracy (±1%)
- ✅ Good stability (σ=0.36)

**CO2:**
- ✅ Minimal overshoot (0%)
- ⚠️ Poor steady-state accuracy (±100%) - increase Ki
- ✅ Excellent stability (σ=0)

**O2:**
- ✅ Minimal overshoot (0%)
- ⚠️ Poor steady-state accuracy (±100%) - increase Ki
- ✅ Excellent stability (σ=0)

### Overall Recommendation
⚠️ **Further tuning recommended.** Review performance metrics and adjust PID parameters as suggested above.

---

## Raw Data

**Run directory:** `run_025_baseline_test/`

**Files:**
- [run_metadata.json](run_metadata.json) - Run configuration and metadata
- [sensor_readings.json](sensor_readings.json) - All sensor data (4 readings)
- [pid_actions.json](pid_actions.json) - PID control actions (5 actions)
- [manual_events.json](manual_events.json) - Operator-logged events (1 events)

**For detailed analysis:** Load these files into your preferred data analysis tool (Python, R, MATLAB, etc.)