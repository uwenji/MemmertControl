# 📦 Memmert Scheduler Package - Files Overview

## ✅ What's Included

I've created a complete system for controlling your Memmert incubator based on JSON schedules. Here's everything you received:

### 🎯 Main Scripts

#### 1. **memmert_scheduler.py** (14 KB)
The core scheduler that executes your setpoint schedules.

**What it does:**
- Reads JSON schedule files
- Monitors time and executes setpoints when scheduled
- Validates values against device ranges
- Handles errors gracefully
- Provides detailed logging

**Usage:**
```bash
python memmert_scheduler.py --ip 192.168.100.100 --schedule data/schedules/setpoint_schedule_2025-09-11T08-35-12.json
```

**Features:**
- Continuous monitoring or single-shot execution
- Configurable check intervals and time tolerance
- Tracks executed setpoints to prevent duplicates
- Shows next scheduled change
- Can run as a service, cron job, or manually

---

#### 2. **test_connection.py** (2 KB)
Quick diagnostic tool to verify your connection works.

**What it does:**
- Tests connection to the incubator
- Displays current readings
- Shows current setpoints
- Shows valid parameter ranges

**Usage:**
```bash
python test_connection.py 192.168.100.100
```

**When to use:**
- First setup
- After network changes
- Troubleshooting connection issues

---

#### 3. **apply_schedule_entry.py** (3.4 KB)
Manual control tool for testing or emergency changes.

**What it does:**
- Loads a schedule file
- Applies one specific entry manually
- Shows before/after state
- Perfect for testing

**Usage:**
```bash
python apply_schedule_entry.py data/schedules/setpoint_schedule_2025-09-11T08-35-12.json 0
```

The `0` means "apply first entry". Change to 1 for second entry, etc.

---

#### 4. **create_schedule_example.py** (11 KB)
Examples for generating custom schedules programmatically.

**What it does:**
- Shows how to create schedules in Python
- Includes 3 example patterns:
  - Simple constant setpoints
  - Temperature ramps (for warming)
  - Cycling schedules (for heat shock)

**Usage:**
```bash
python create_schedule_example.py
```

This creates 3 example schedules in `data/schedules/`.

---

### 📚 Documentation

#### 5. **QUICK_START.md** (6 KB)
Step-by-step guide to get up and running in 5 minutes.

**Contents:**
- Setup checklist
- Test procedures
- Common commands
- Background service setup
- Troubleshooting

**Start here!** This is your first stop after downloading.

---

#### 6. **SCHEDULER_README.md** (7 KB)
Complete reference documentation.

**Contents:**
- All command-line options
- Schedule file format
- How it works internally
- Error handling
- Advanced usage
- Running as systemd service

---

## 🚀 Quick Setup (3 Steps)

### Step 1: Copy Files to Your Pi
```bash
cd ~/MemmertControl
# Copy the 4 Python scripts here
# Copy the 2 markdown files for reference
```

### Step 2: Test Connection
```bash
python test_connection.py 192.168.100.100
```

### Step 3: Run Your Schedule
```bash
# Test mode (runs once, shows what it would do)
python memmert_scheduler.py --once

# For real (runs continuously)
python memmert_scheduler.py
```

---

## 📋 File Structure in Your Project

After setup, your folder should look like:

```
MemmertControl/
├── atmoweb.py                    # (your existing file)
├── memmert_scheduler.py          # ← NEW: Main scheduler
├── test_connection.py            # ← NEW: Connection tester
├── apply_schedule_entry.py       # ← NEW: Manual control
├── create_schedule_example.py    # ← NEW: Schedule generator
├── QUICK_START.md                # ← NEW: Quick guide
├── SCHEDULER_README.md           # ← NEW: Full docs
├── data/
│   └── schedules/
│       └── setpoint_schedule_2025-09-11T08-35-12.json  # (your existing)
├── logs/                         # Create this for logs
└── ... (your other files)
```

---

## 🎓 Usage Examples

### Basic Usage
```bash
# Run with default settings
python memmert_scheduler.py

# Run with custom IP
python memmert_scheduler.py --ip 192.168.1.50

# Run for 24 hours then stop
python memmert_scheduler.py --duration 24

# Check every 10 seconds (more responsive)
python memmert_scheduler.py --check-interval 10
```

### Background Execution
```bash
# Option 1: Screen (simplest)
screen -S memmert
python memmert_scheduler.py
# Press Ctrl+A then D to detach

# Option 2: Nohup
nohup python memmert_scheduler.py > logs/scheduler.log 2>&1 &

# Option 3: Cron (runs every minute)
* * * * * cd /home/pi/MemmertControl && python memmert_scheduler.py --once >> logs/scheduler.log 2>&1
```

### Testing
```bash
# Test connection
python test_connection.py

# Test a single schedule entry manually
python apply_schedule_entry.py data/schedules/setpoint_schedule_2025-09-11T08-35-12.json 0

# Dry run (shows what would happen)
python memmert_scheduler.py --once --verbose

# Generate example schedules
python create_schedule_example.py
```

---

## 🔍 What Each File Does - At a Glance

| File | Size | Purpose | Use When |
|------|------|---------|----------|
| `memmert_scheduler.py` | 14 KB | Main scheduler | Running experiments |
| `test_connection.py` | 2 KB | Test connection | First time, troubleshooting |
| `apply_schedule_entry.py` | 3.4 KB | Manual control | Testing, emergencies |
| `create_schedule_example.py` | 11 KB | Generate schedules | Need custom patterns |
| `QUICK_START.md` | 6 KB | Getting started guide | First time setup |
| `SCHEDULER_README.md` | 7 KB | Full documentation | Reference, advanced use |

---

## 💡 Key Features

✅ **Automatic scheduling** - Set it and forget it  
✅ **Range validation** - Won't set invalid values  
✅ **Error handling** - Graceful degradation if parameters unavailable  
✅ **Flexible execution** - Continuous, duration-limited, or cron  
✅ **Detailed logging** - Know exactly what happened and when  
✅ **Time tolerance** - Won't miss changes due to slight timing  
✅ **Easy testing** - Multiple tools for validation  
✅ **Well documented** - Extensive guides and examples  

---

## 🐛 Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| Connection refused | Enable Remote Control on incubator |
| Parameter not available | Normal if device doesn't have feature |
| No setpoints executing | Check timestamps are in future |
| Values not changing | Check permission level (needs "Write") |
| Schedule not loading | Validate JSON syntax |

---

## 📞 Next Steps

1. **Read** `QUICK_START.md` for step-by-step setup
2. **Run** `test_connection.py` to verify connection  
3. **Test** with `apply_schedule_entry.py` to apply one setpoint
4. **Execute** with `memmert_scheduler.py` to run your schedule
5. **Customize** using `create_schedule_example.py` as template

---

## 🎉 Success Indicators

You'll know everything is working when you see:

```
2025-10-22 10:00:15 - INFO - Starting scheduler...
2025-10-22 10:00:15 - INFO - Loaded schedule with 14 setpoints
============================================================
2025-10-22 11:00:05 - INFO - Executing scheduled setpoints at 2025-10-22 11:00:00
============================================================
2025-10-22 11:00:06 - INFO - ✓ Set TempSet=25.0 (actual: 25.0)
2025-10-22 11:00:06 - INFO - ✓ Set HumSet=40.0 (actual: 40.0)
2025-10-22 11:00:07 - INFO - Execution summary:
2025-10-22 11:00:07 - INFO -   Success: 4/4
```

Happy automating! 🚀

---

*All files created based on your existing `atmoweb.py` and schedule JSON. Compatible with Memmert generation 2012 climate chambers with AtmoWEB REST interface.*
