#!/usr/bin/env python3
"""
Debug and test schedule watcher
"""
import os
from pathlib import Path
from datetime import datetime

SCHEDULE_FILE = Path("data/schedules/setpoint_schedule.json")
LAST_MODIFIED_FILE = Path("data/.schedule_last_modified")

print("=" * 60)
print("SCHEDULE WATCHER DEBUG")
print("=" * 60)

# Check schedule file
if SCHEDULE_FILE.exists():
    mtime = os.path.getmtime(SCHEDULE_FILE)
    mtime_readable = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
    print(f"✓ Schedule file exists: {SCHEDULE_FILE}")
    print(f"  Modified: {mtime_readable}")
    print(f"  Timestamp: {mtime}")
else:
    print(f"✗ Schedule file NOT found: {SCHEDULE_FILE}")

print()

# Check tracking file
if LAST_MODIFIED_FILE.exists():
    with open(LAST_MODIFIED_FILE, 'r') as f:
        last_mtime = float(f.read().strip())
    last_mtime_readable = datetime.fromtimestamp(last_mtime).strftime('%Y-%m-%d %H:%M:%S')
    print(f"✓ Tracking file exists: {LAST_MODIFIED_FILE}")
    print(f"  Last seen: {last_mtime_readable}")
    print(f"  Timestamp: {last_mtime}")
else:
    print(f"✗ Tracking file NOT found: {LAST_MODIFIED_FILE}")

print()

# Compare
if SCHEDULE_FILE.exists() and LAST_MODIFIED_FILE.exists():
    mtime = os.path.getmtime(SCHEDULE_FILE)
    with open(LAST_MODIFIED_FILE, 'r') as f:
        last_mtime = float(f.read().strip())
    
    if mtime > last_mtime:
        print("✓ Schedule has CHANGED - watcher will trigger!")
    else:
        print("✗ Schedule has NOT changed - watcher will skip")
        print(f"  Time difference: {mtime - last_mtime:.2f} seconds")

print()
print("=" * 60)
print("OPTIONS:")
print("=" * 60)
print("1. Touch file to trigger:  touch data/schedules/setpoint_schedule.json")
print("2. Reset tracker:          rm data/.schedule_last_modified")
print("3. Edit and save schedule: nano data/schedules/setpoint_schedule.json")
print()
