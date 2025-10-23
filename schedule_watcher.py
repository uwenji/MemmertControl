#!/usr/bin/env python3
"""
Schedule Watcher - Runs scheduler when schedule file changes
"""
import os
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Configuration
SCHEDULE_FILE = Path("data/schedules/setpoint_schedule.json")
LAST_MODIFIED_FILE = Path("data/.schedule_last_modified")
SCHEDULER_SCRIPT = Path("memmert_scheduler.py")
INCUBATOR_IP = "192.168.100.100"


def get_file_modified_time(file_path):
    """Get file modification timestamp."""
    if not file_path.exists():
        return None
    return os.path.getmtime(file_path)


def load_last_modified():
    """Load last known modification time."""
    if not LAST_MODIFIED_FILE.exists():
        return None
    try:
        with open(LAST_MODIFIED_FILE, 'r') as f:
            return float(f.read().strip())
    except:
        return None


def save_last_modified(timestamp):
    """Save modification time."""
    LAST_MODIFIED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LAST_MODIFIED_FILE, 'w') as f:
        f.write(str(timestamp))


def run_scheduler():
    """Run the scheduler with the current schedule."""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Schedule updated! Running scheduler...")
    
    try:
        result = subprocess.run(
            [sys.executable, str(SCHEDULER_SCRIPT), 
             '--schedule', str(SCHEDULE_FILE),
             '--ip', INCUBATOR_IP,
             '--once'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print(f"✓ Scheduler executed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"✗ Scheduler failed")
            if result.stderr:
                print(result.stderr)
                
    except Exception as e:
        print(f"✗ Error running scheduler: {e}")


def main():
    """Main watcher logic."""
    # Get current modification time
    current_mtime = get_file_modified_time(SCHEDULE_FILE)
    
    if current_mtime is None:
        print(f"Schedule file not found: {SCHEDULE_FILE}")
        return 1
    
    # Get last known modification time
    last_mtime = load_last_modified()
    
    # Check if file changed
    if last_mtime is None or current_mtime > last_mtime:
        # File is new or has been modified
        run_scheduler()
        save_last_modified(current_mtime)
    else:
        # No changes
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No changes to schedule")
    
    return 0


if __name__ == '__main__':
    exit(main())
