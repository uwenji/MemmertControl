# Run Report: run_032_test4

**Status:** ✅ COMPLETED  
**Date:** 31.10.2025  
**Duration:** 20 minutes  
**Type:** door_opening

---

## Executive Summary

**Run Name:** test4  
**Description:** undefined

**Key Findings:**
- **Data Quality:** Fair (64.36% complete)
- **Total Readings:** 13
- **PID Actions:** 20
- **Disturbances:** 0

**Temp:**
- Steady-state error: ±1.38°C
- Stability (σ): 0.44°C

**Hum:**
- Settling time: 0.6 minutes
- Overshoot: 51.7%
- Steady-state error: ±9.46%
- Stability (σ): 12.33%

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
| 00:06:26 | custom | general | - |
| 00:14:07 | custom | general | - |
| 00:20:09 | system | run_stop | - |
| 00:20:11 | Run ended | system | completed |

---

## Performance Metrics

### Temp

**Target:** 30°C

**Time-Domain Response:**
- Initial value: 28.93°C
- Final value: 28.6°C
- Peak time: 4.2 minutes
- Peak value: 28.96°C
- Overshoot: 0%
- Settling time (±5%): 0.6 minutes

**Steady-State Performance** (last 17 minutes):
- Mean: 28.62°C
- Standard deviation: 0.44°C
- Range: 1.6°C (27.36 to 28.96)
- Steady-state error: 1.38°C (4.6%)

### Hum

**Target:** 60%

**Time-Domain Response:**
- Initial value: 60.33%
- Final value: 59.18%
- Peak time: 14.2 minutes
- Peak value: 29.01%
- Overshoot: 51.7%
- Settling time (±2%): 0.6 minutes
- Settling time (±5%): 0.6 minutes

**Steady-State Performance** (last 17 minutes):
- Mean: 50.54%
- Standard deviation: 12.33%
- Range: 36.04% (29.01 to 65.04)
- Steady-state error: 9.46% (15.8%)

### CO2

**Target:** 1000 ppm

**Time-Domain Response:**
- Initial value: 0 ppm
- Final value: 0 ppm
- Overshoot: 0%

**Steady-State Performance** (last 17 minutes):
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

**Steady-State Performance** (last 17 minutes):
- Mean: 0%
- Standard deviation: 0%
- Range: 0% (0 to 0)
- Steady-state error: 21% (100%)

---

## Disturbance Analysis

No disturbances detected or analyzed.

---

## Data Quality

**Completeness:** 64.36% (Fair)
- Expected readings: 20.2
- Actual readings: 13
- Missed readings: 7.2

**Sensor Status:**
All sensors operational

---

## Conclusions and Recommendations

### Performance Assessment

**Temp:**
- ✅ Minimal overshoot (0%)
- ✅ Good steady-state accuracy (±4.6%)
- ✅ Good stability (σ=0.44)

**Hum:**
- ✅ Good settling time (0.6 min)
- ⚠️ High overshoot (51.7%) - reduce Kp
- ⚠️ Poor steady-state accuracy (±15.8%) - increase Ki
- ⚠️ Poor stability (σ=12.33) - check for oscillations

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

**Run directory:** `run_032_test4/`

**Files:**
- [run_metadata.json](run_metadata.json) - Run configuration and metadata
- [sensor_readings.json](sensor_readings.json) - All sensor data (readings)
- [pid_actions.json](pid_actions.json) - PID control actions (setpoint calculations)
- [manual_events.json](manual_events.json) - Operator-logged events and observations
- [setpoint_schedule.json](setpoint_schedule.json) - PID-generated setpoint schedule (time-filtered)
- [target_schedule.json](target_schedule.json) - User-defined target schedule (time-filtered)
- [run_report.md](run_report.md) - This report

**For detailed analysis:** Load these files into your preferred data analysis tool (Python, R, MATLAB, etc.)