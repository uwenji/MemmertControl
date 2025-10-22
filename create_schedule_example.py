#!/usr/bin/env python3
"""
Example: Create a custom setpoint schedule programmatically.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path


def create_simple_schedule(
    output_file,
    start_time=None,
    duration_hours=24,
    interval_hours=2,
    temp=25.0,
    humidity=40.0,
    co2=400,
    fan=50
):
    """
    Create a simple schedule with constant setpoints at regular intervals.
    
    Args:
        output_file: Where to save the schedule JSON
        start_time: When to start (defaults to now)
        duration_hours: How many hours to schedule
        interval_hours: Hours between setpoint changes
        temp: Temperature setpoint (°C)
        humidity: Humidity setpoint (% RH)
        co2: CO2 setpoint (ppm)
        fan: Fan speed (%)
    """
    if start_time is None:
        start_time = datetime.now()
    
    schedule_entries = []
    current_time = start_time
    end_time = start_time + timedelta(hours=duration_hours)
    
    while current_time <= end_time:
        entry = {
            "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "setpoints": {
                "TempSet": temp,
                "HumSet": humidity,
                "CO2Set": co2,
                "FanSet": fan
            }
        }
        schedule_entries.append(entry)
        current_time += timedelta(hours=interval_hours)
    
    schedule = {
        "metadata": {
            "generated": datetime.now().isoformat() + "Z",
            "generatedBy": "create_schedule_example.py",
            "version": "1.0",
            "description": "Simple constant setpoint schedule"
        },
        "configuration": {
            "categories": ["Temperature", "Humidity", "CO2", "Fan"],
            "timeZone": "UTC",
            "futureHours": duration_hours
        },
        "schedule": schedule_entries,
        "statistics": {
            "totalPoints": len(schedule_entries),
            "timeSpan": f"{duration_hours} hours",
            "interval": f"{interval_hours} hours",
            "variableRanges": {
                "TempSet": {"min": temp, "max": temp, "average": temp},
                "HumSet": {"min": humidity, "max": humidity, "average": humidity},
                "CO2Set": {"min": co2, "max": co2, "average": co2},
                "FanSet": {"min": fan, "max": fan, "average": fan}
            }
        }
    }
    
    # Save to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(schedule, f, indent=2)
    
    print(f"Created schedule: {output_file}")
    print(f"  Total entries: {len(schedule_entries)}")
    print(f"  Start: {schedule_entries[0]['timestamp']}")
    print(f"  End: {schedule_entries[-1]['timestamp']}")
    print(f"  Setpoints: Temp={temp}°C, Humidity={humidity}%, CO2={co2}ppm, Fan={fan}%")


def create_ramp_schedule(
    output_file,
    start_time=None,
    temp_start=20.0,
    temp_end=37.0,
    ramp_hours=4,
    hold_hours=20,
    interval_minutes=30
):
    """
    Create a temperature ramp schedule (e.g., for warming up cell cultures).
    
    Args:
        output_file: Where to save the schedule JSON
        start_time: When to start (defaults to now)
        temp_start: Starting temperature (°C)
        temp_end: Ending temperature (°C)
        ramp_hours: Hours to ramp from start to end
        hold_hours: Hours to hold at end temperature
        interval_minutes: Minutes between setpoint changes
    """
    if start_time is None:
        start_time = datetime.now()
    
    schedule_entries = []
    
    # Calculate ramp
    total_ramp_minutes = ramp_hours * 60
    num_ramp_points = int(total_ramp_minutes / interval_minutes)
    temp_step = (temp_end - temp_start) / num_ramp_points
    
    # Ramp phase
    current_time = start_time
    current_temp = temp_start
    
    for i in range(num_ramp_points + 1):
        entry = {
            "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "setpoints": {
                "TempSet": round(current_temp, 1),
                "HumSet": 60.0,
                "CO2Set": 5.0,
                "FanSet": 50
            }
        }
        schedule_entries.append(entry)
        
        current_time += timedelta(minutes=interval_minutes)
        current_temp += temp_step
    
    # Hold phase
    hold_end = current_time + timedelta(hours=hold_hours)
    
    while current_time <= hold_end:
        entry = {
            "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "setpoints": {
                "TempSet": temp_end,
                "HumSet": 60.0,
                "CO2Set": 5.0,
                "FanSet": 50
            }
        }
        schedule_entries.append(entry)
        current_time += timedelta(minutes=interval_minutes)
    
    schedule = {
        "metadata": {
            "generated": datetime.now().isoformat() + "Z",
            "generatedBy": "create_schedule_example.py",
            "version": "1.0",
            "description": f"Temperature ramp from {temp_start}°C to {temp_end}°C over {ramp_hours}h, hold {hold_hours}h"
        },
        "configuration": {
            "categories": ["Temperature", "Humidity", "CO2", "Fan"],
            "timeZone": "UTC",
            "futureHours": ramp_hours + hold_hours
        },
        "schedule": schedule_entries,
        "statistics": {
            "totalPoints": len(schedule_entries),
            "rampPhase": f"{ramp_hours} hours",
            "holdPhase": f"{hold_hours} hours",
            "variableRanges": {
                "TempSet": {
                    "min": temp_start,
                    "max": temp_end,
                    "average": (temp_start + temp_end) / 2
                }
            }
        }
    }
    
    # Save to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(schedule, f, indent=2)
    
    print(f"Created ramp schedule: {output_file}")
    print(f"  Total entries: {len(schedule_entries)}")
    print(f"  Ramp: {temp_start}°C → {temp_end}°C over {ramp_hours}h")
    print(f"  Hold: {temp_end}°C for {hold_hours}h")
    print(f"  Interval: {interval_minutes} minutes")


def create_cycling_schedule(
    output_file,
    start_time=None,
    temp_high=37.0,
    temp_low=25.0,
    cycle_hours=4,
    num_cycles=6
):
    """
    Create a cycling schedule (e.g., for heat shock experiments).
    
    Args:
        output_file: Where to save the schedule JSON
        start_time: When to start (defaults to now)
        temp_high: High temperature (°C)
        temp_low: Low temperature (°C)
        cycle_hours: Hours per cycle
        num_cycles: Number of cycles to perform
    """
    if start_time is None:
        start_time = datetime.now()
    
    schedule_entries = []
    current_time = start_time
    
    for cycle in range(num_cycles):
        # High temperature
        entry_high = {
            "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "setpoints": {
                "TempSet": temp_high,
                "HumSet": 50.0,
                "FanSet": 50
            }
        }
        schedule_entries.append(entry_high)
        
        current_time += timedelta(hours=cycle_hours / 2)
        
        # Low temperature
        entry_low = {
            "timestamp": current_time.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "setpoints": {
                "TempSet": temp_low,
                "HumSet": 50.0,
                "FanSet": 50
            }
        }
        schedule_entries.append(entry_low)
        
        current_time += timedelta(hours=cycle_hours / 2)
    
    schedule = {
        "metadata": {
            "generated": datetime.now().isoformat() + "Z",
            "generatedBy": "create_schedule_example.py",
            "version": "1.0",
            "description": f"Cycling between {temp_low}°C and {temp_high}°C, {num_cycles} cycles"
        },
        "configuration": {
            "categories": ["Temperature", "Humidity", "Fan"],
            "timeZone": "UTC",
            "futureHours": cycle_hours * num_cycles
        },
        "schedule": schedule_entries,
        "statistics": {
            "totalPoints": len(schedule_entries),
            "cycles": num_cycles,
            "cycleLength": f"{cycle_hours} hours",
            "variableRanges": {
                "TempSet": {
                    "min": temp_low,
                    "max": temp_high,
                    "average": (temp_low + temp_high) / 2
                }
            }
        }
    }
    
    # Save to file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(schedule, f, indent=2)
    
    print(f"Created cycling schedule: {output_file}")
    print(f"  Total entries: {len(schedule_entries)}")
    print(f"  Cycles: {num_cycles}")
    print(f"  Temperature: {temp_low}°C ↔ {temp_high}°C")
    print(f"  Cycle length: {cycle_hours} hours")


if __name__ == '__main__':
    import sys
    
    print("Memmert Schedule Generator")
    print("=" * 60)
    
    # Create output directory
    output_dir = Path("data/schedules")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Example 1: Simple constant schedule
    print("\n1. Creating simple constant schedule...")
    create_simple_schedule(
        output_file=output_dir / "simple_schedule.json",
        start_time=datetime.now() + timedelta(hours=1),
        duration_hours=24,
        interval_hours=2,
        temp=25.0,
        humidity=40.0,
        co2=400,
        fan=50
    )
    
    # Example 2: Temperature ramp (e.g., for cell culture)
    print("\n2. Creating temperature ramp schedule...")
    create_ramp_schedule(
        output_file=output_dir / "ramp_schedule.json",
        start_time=datetime.now() + timedelta(hours=1),
        temp_start=20.0,
        temp_end=37.0,
        ramp_hours=4,
        hold_hours=20,
        interval_minutes=30
    )
    
    # Example 3: Cycling schedule (e.g., for heat shock)
    print("\n3. Creating cycling schedule...")
    create_cycling_schedule(
        output_file=output_dir / "cycling_schedule.json",
        start_time=datetime.now() + timedelta(hours=1),
        temp_high=37.0,
        temp_low=25.0,
        cycle_hours=4,
        num_cycles=6
    )
    
    print("\n" + "=" * 60)
    print("✓ All example schedules created in data/schedules/")
    print("\nTo use:")
    print("  python memmert_scheduler.py --schedule data/schedules/simple_schedule.json")
    print("  python memmert_scheduler.py --schedule data/schedules/ramp_schedule.json")
    print("  python memmert_scheduler.py --schedule data/schedules/cycling_schedule.json")
