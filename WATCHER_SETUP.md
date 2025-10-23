# Schedule Auto-Update Setup

## What It Does

Checks `setpoint_schedule.json` every minute. If it's been updated, automatically runs the scheduler with the new schedule.

## Setup (3 Steps)

### Step 1: Copy the watcher

```bash
cd ~/Desktop/MemmertControl
# File is already there: schedule_watcher.py
```

### Step 2: Test it

```bash
# Test the watcher
python schedule_watcher.py

# Should say: "No changes to schedule" (if schedule hasn't changed)
```

### Step 3: Add to cron

```bash
crontab -e

# Add this line (runs every minute):
* * * * * cd /home/pi/Desktop/MemmertControl && /usr/bin/python3 schedule_watcher.py >> logs/watcher.log 2>&1
```

## That's It!

Now:
- Edit `data/schedules/setpoint_schedule.json`
- Save it
- Within 1 minute, scheduler automatically applies the new schedule

## Monitor It

```bash
# Watch the watcher logs
tail -f logs/watcher.log

# When you update schedule, you'll see:
# [2025-10-23 10:05:00] Schedule updated! Running scheduler...
# ✓ Scheduler executed successfully
```

## Your Complete Cron Setup

```bash
crontab -l

# Should show 2 lines:
* * * * * cd /home/pi/Desktop/MemmertControl && /usr/bin/python3 memmert_logger.py >> logs/logger.log 2>&1
* * * * * cd /home/pi/Desktop/MemmertControl && /usr/bin/python3 schedule_watcher.py >> logs/watcher.log 2>&1
```

Done! 🎉
