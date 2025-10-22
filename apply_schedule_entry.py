#!/usr/bin/env python3
"""
Example: Manually apply a specific scheduled setpoint.
Useful for testing or emergency manual control.
"""
import json
from pathlib import Path
from archive.atmoweb import AtmoWebClient

def apply_schedule_entry(ip, schedule_file, entry_index=0):
    """
    Apply a specific entry from a schedule file.
    
    Args:
        ip: IP address of the device
        schedule_file: Path to schedule JSON file
        entry_index: Which entry to apply (0 = first)
    """
    print(f"Loading schedule from: {schedule_file}")
    
    # Load schedule
    with open(schedule_file, 'r') as f:
        schedule = json.load(f)
    
    if 'schedule' not in schedule or not schedule['schedule']:
        print("Error: No schedule entries found")
        return
    
    # Get the specific entry
    if entry_index >= len(schedule['schedule']):
        print(f"Error: Entry {entry_index} not found. Schedule has {len(schedule['schedule'])} entries.")
        return
    
    entry = schedule['schedule'][entry_index]
    timestamp = entry['timestamp']
    setpoints = entry.get('setpoints', {})
    
    print(f"\nApplying setpoints from entry {entry_index}")
    print(f"Scheduled for: {timestamp}")
    print(f"Setpoints: {setpoints}")
    print("-" * 60)
    
    # Create client
    client = AtmoWebClient(ip=ip)
    
    # Apply each setpoint
    results = []
    for key, value in setpoints.items():
        try:
            actual = client.set_parameter(key, value)
            status = "✓"
            message = f"{key}={value} (actual: {actual})"
            results.append((status, message))
            print(f"{status} {message}")
            
        except ValueError as e:
            status = "✗"
            message = f"{key}={value} - {e}"
            results.append((status, message))
            print(f"{status} {message}")
            
        except KeyError as e:
            status = "⚠"
            message = f"{key}={value} - Not available on device"
            results.append((status, message))
            print(f"{status} {message}")
    
    # Summary
    print("-" * 60)
    success_count = sum(1 for r in results if r[0] == "✓")
    print(f"Applied {success_count}/{len(setpoints)} setpoints successfully")
    
    # Show current state
    print("\nCurrent device state:")
    readings = client.get_readings()
    setpoints_current = client.get_setpoints()
    
    print("  Setpoints:")
    for key, value in setpoints_current.items():
        if value is not None:
            print(f"    {key}: {value}")
    
    print("  Readings:")
    for key, value in readings.items():
        if value is not None:
            print(f"    {key}: {value}")


if __name__ == '__main__':
    import sys
    
    # Get arguments
    if len(sys.argv) < 2:
        print("Usage: python apply_schedule_entry.py <schedule_file> [entry_index] [ip]")
        print("\nExample:")
        print("  python apply_schedule_entry.py data/schedules/setpoint_schedule_2025-09-11T08-35-12.json 0")
        print("\nThis will apply the first entry (index 0) from the schedule.")
        sys.exit(1)
    
    schedule_file = Path(sys.argv[1])
    entry_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    ip = sys.argv[3] if len(sys.argv) > 3 else '192.168.100.100'
    
    try:
        apply_schedule_entry(ip, schedule_file, entry_index)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
