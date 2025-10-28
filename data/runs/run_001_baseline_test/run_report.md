# Run Report: run_001_baseline_test

**Status:** 🔄 RUNNING  
**Date:** 27.10.2025  
**Duration:** 0 minutes  
**Type:** baseline

---

## Executive Summary

**Run Name:** baseline_test  
**Description:** undefined

**Key Findings:**
- **Data Quality:** No data (0% complete)
- **Total Readings:** 0
- **PID Actions:** 1
- **Disturbances:** 0

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

No manual events recorded.

---

## Performance Metrics

---

## Disturbance Analysis

No disturbances detected or analyzed.

---

## Data Quality

**Completeness:** 0% (No data)
- Expected readings: undefined
- Actual readings: undefined
- Missed readings: 0

**Sensor Status:**
All sensors operational

---

## Conclusions and Recommendations

### Performance Assessment

### Overall Recommendation
⚠️ **Further tuning recommended.** Review performance metrics and adjust PID parameters as suggested above.

---

## Raw Data

**Run directory:** `run_001_baseline_test/`

**Files:**
- [run_metadata.json](run_metadata.json) - Run configuration and metadata
- [sensor_readings.json](sensor_readings.json) - All sensor data (0 readings)
- [pid_actions.json](pid_actions.json) - PID control actions (1 actions)
- [manual_events.json](manual_events.json) - Operator-logged events (0 events)

**For detailed analysis:** Load these files into your preferred data analysis tool (Python, R, MATLAB, etc.)