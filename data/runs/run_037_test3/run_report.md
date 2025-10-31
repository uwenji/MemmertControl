# Run Report: run_037_test3

**Status:** ✅ COMPLETED  
**Date:** 31.10.2025  
**Duration:** 146 minutes  
**Type:** step_response

---

## Executive Summary

**Run Name:** test3  
**Description:** undefined

**Key Findings:**
- **Data Quality:** Fair (72.41% complete)
- **Total Readings:** 106
- **PID Actions:** 146
- **Disturbances:** 0

**Temp:**
- Steady-state error: ±4.3°C
- Stability (σ): 0.34°C

**Hum:**
- Overshoot: 21.2%
- Steady-state error: ±0.24%
- Stability (σ): 0.45%

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
| Temp | 0.6 / 1.2 (up/down) | 0.03 / 0.08 (up/down) | 0.15 / 0.3 (up/down) |
| Hum | 0.4 / 1 (up/down) | 0.02 / 0.06 (up/down) | 0.1 / 0.25 (up/down) |
| CO2 | 0.3 | 0.01 | 0.05 |
| O2 | 0.5 | 0.02 | 0.1 |
| Fan | 0.5 | 0.05 | 0.02 |

---

## Timeline

| Time | Event | Category | Notes |
|------|-------|----------|-------|
| 00:00:00 | Run started | system | - |
| 00:05:58 | custom | general | - |
| 00:30:39 | custom | general | - |
| 00:41:24 | custom | general | - |
| 00:41:37 | custom | general | - |
| 02:26:20 | system | run_stop | - |
| 02:26:23 | Run ended | system | completed |

---

## Performance Metrics

### Temp

**Target:** 30°C

**Time-Domain Response:**
- Initial value: 30.51°C
- Final value: 33.79°C
- Overshoot: 0%

**Steady-State Performance** (last 30 minutes):
- Mean: 34.3°C
- Standard deviation: 0.34°C
- Range: 1.17°C (33.65 to 34.82)
- Steady-state error: 4.3°C (14.3%)

### Hum

**Target:** 60%

**Time-Domain Response:**
- Initial value: 59.82%
- Final value: 60.67%
- Peak time: 34.3 minutes
- Peak value: 72.71%
- Overshoot: 21.2%
- Settling time (±5%): 0.3 minutes

**Steady-State Performance** (last 30 minutes):
- Mean: 60.24%
- Standard deviation: 0.45%
- Range: 1.39% (59.56 to 60.95)
- Steady-state error: 0.24% (0.4%)

### CO2

**Target:** 1000 ppm

**Time-Domain Response:**
- Initial value: 0 ppm
- Final value: 0 ppm
- Overshoot: 0%

**Steady-State Performance** (last 30 minutes):
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

**Steady-State Performance** (last 30 minutes):
- Mean: 0%
- Standard deviation: 0%
- Range: 0% (0 to 0)
- Steady-state error: 21% (100%)

---

## Disturbance Analysis

No disturbances detected or analyzed.

---

## Data Quality

**Completeness:** 72.41% (Fair)
- Expected readings: 146.4
- Actual readings: 106
- Missed readings: 40.4

**Sensor Status:**
All sensors operational

---

## Conclusions and Recommendations

### Performance Assessment

**Temp:**
- ✅ Minimal overshoot (0%)
- ⚠️ Poor steady-state accuracy (±14.3%) - increase Ki
- ✅ Good stability (σ=0.34)

**Hum:**
- ⚠️ High overshoot (21.2%) - reduce Kp
- ✅ Excellent steady-state accuracy (±0.4%)
- ✅ Good stability (σ=0.45)

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

**Run directory:** `run_037_test3/`

**Files:**
- [run_metadata.json](run_metadata.json) - Run configuration and metadata
- [sensor_readings.json](sensor_readings.json) - All sensor data (readings)
- [pid_actions.json](pid_actions.json) - PID control actions (setpoint calculations)
- [manual_events.json](manual_events.json) - Operator-logged events and observations
- [setpoint_schedule.json](setpoint_schedule.json) - PID-generated setpoint schedule (time-filtered)
- [target_schedule.json](target_schedule.json) - User-defined target schedule (time-filtered)
- [run_report.md](run_report.md) - This report

**For detailed analysis:** Load these files into your preferred data analysis tool (Python, R, MATLAB, etc.)