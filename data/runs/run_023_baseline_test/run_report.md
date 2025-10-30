# Run Report: run_023_baseline_test

**Status:** ✅ COMPLETED  
**Date:** 30.10.2025  
**Duration:** 3 minutes  
**Type:** baseline

---

## Executive Summary

**Run Name:** baseline_test  
**Description:** undefined

**Key Findings:**
- **Data Quality:** Fair (1.44% complete)
- **Total Readings:** 3
- **PID Actions:** 5
- **Disturbances:** 0

**Temp:**
- Settling time: 0.6 minutes
- Steady-state error: ±0.01°C
- Stability (σ): 0.02°C

**Hum:**
- Settling time: 0.6 minutes
- Steady-state error: ±0.41%
- Stability (σ): 0.22%

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
| 00:03:29 | Run ended | system | completed |

---

## Performance Metrics

### Temp

**Target:** 30°C

**Time-Domain Response:**
- Initial value: 29.97°C
- Final value: 30.01°C
- Rise time (10-90%): 1.2 minutes
- Peak time: 3.5 minutes
- Peak value: 30.01°C
- Overshoot: 0%
- Settling time (±2%): 0.6 minutes
- Settling time (±5%): 0.6 minutes

**Steady-State Performance** (last 3 minutes):
- Mean: 29.99°C
- Standard deviation: 0.02°C
- Range: 0.04°C (29.97 to 30.01)
- Steady-state error: 0.01°C (0%)

### Hum

**Target:** 60%

**Time-Domain Response:**
- Initial value: 60.67%
- Final value: 60.14%
- Peak time: 3.5 minutes
- Peak value: 60.14%
- Overshoot: 0%
- Settling time (±2%): 0.6 minutes
- Settling time (±5%): 0.6 minutes

**Steady-State Performance** (last 3 minutes):
- Mean: 60.41%
- Standard deviation: 0.22%
- Range: 0.53% (60.14 to 60.67)
- Steady-state error: 0.41% (0.7%)

### CO2

**Target:** 1000 ppm

**Time-Domain Response:**
- Initial value: 0 ppm
- Final value: 0 ppm
- Overshoot: 0%

**Steady-State Performance** (last 3 minutes):
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

**Steady-State Performance** (last 3 minutes):
- Mean: 0%
- Standard deviation: 0%
- Range: 0% (0 to 0)
- Steady-state error: 21% (100%)

---

## Disturbance Analysis

No disturbances detected or analyzed.

---

## Data Quality

**Completeness:** 1.44% (Fair)
- Expected readings: 209
- Actual readings: 3
- Missed readings: 206

**Sensor Status:**
All sensors operational

---

## Conclusions and Recommendations

### Performance Assessment

**Temp:**
- ✅ Good settling time (0.6 min)
- ✅ Minimal overshoot (0%)
- ✅ Excellent steady-state accuracy (±0%)
- ✅ Excellent stability (σ=0.02)

**Hum:**
- ✅ Good settling time (0.6 min)
- ✅ Minimal overshoot (0%)
- ✅ Excellent steady-state accuracy (±0.7%)
- ✅ Excellent stability (σ=0.22)

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

**Run directory:** `run_023_baseline_test/`

**Files:**
- [run_metadata.json](run_metadata.json) - Run configuration and metadata
- [sensor_readings.json](sensor_readings.json) - All sensor data (3 readings)
- [pid_actions.json](pid_actions.json) - PID control actions (5 actions)
- [manual_events.json](manual_events.json) - Operator-logged events (1 events)

**For detailed analysis:** Load these files into your preferred data analysis tool (Python, R, MATLAB, etc.)