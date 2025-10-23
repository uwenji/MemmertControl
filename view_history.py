#!/usr/bin/env python3
"""
View and analyze Memmert incubator history data.
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional
import argparse


def load_history(log_file: Path) -> dict:
    """Load history from JSON file."""
    if not log_file.exists():
        print(f"Error: Log file not found: {log_file}")
        sys.exit(1)
    
    with open(log_file, 'r') as f:
        return json.load(f)


def print_summary(history: dict):
    """Print summary of the log file."""
    metadata = history.get('metadata', {})
    data = history.get('data', [])
    
    print("=" * 70)
    print("INCUBATOR HISTORY SUMMARY")
    print("=" * 70)
    print(f"Device IP: {metadata.get('device_ip', 'Unknown')}")
    print(f"Created: {metadata.get('created', 'Unknown')}")
    print(f"Last Updated: {metadata.get('last_updated', 'Unknown')}")
    print(f"Max Hours: {metadata.get('max_hours', 'Unknown')}")
    print(f"Total Entries: {metadata.get('total_entries', len(data))}")
    print(f"Time Span: {metadata.get('time_span_hours', 'Unknown')} hours")
    
    if data:
        first = data[0]['timestamp']
        last = data[-1]['timestamp']
        print(f"First Entry: {first}")
        print(f"Last Entry: {last}")
    
    print("=" * 70)


def print_latest(history: dict, count: int = 5):
    """Print latest N entries."""
    data = history.get('data', [])
    
    if not data:
        print("No data available")
        return
    
    print(f"\nLATEST {min(count, len(data))} ENTRIES:")
    print("-" * 70)
    
    for entry in data[-count:]:
        timestamp = entry.get('timestamp', 'Unknown')
        mode = entry.get('mode', 'Unknown')
        readings = entry.get('readings', {})
        setpoints = entry.get('setpoints', {})
        
        print(f"\n[{timestamp}] Mode: {mode}")
        
        # Temperature
        temp_read = readings.get('Temp1Read')
        temp_set = setpoints.get('TempSet')
        if temp_read is not None:
            print(f"  Temperature: {temp_read:.1f}°C (setpoint: {temp_set}°C)")
        
        # Humidity
        hum_read = readings.get('HumRead')
        hum_set = setpoints.get('HumSet')
        if hum_read is not None:
            print(f"  Humidity: {hum_read:.1f}% (setpoint: {hum_set}%)")
        
        # CO2
        co2_read = readings.get('CO2Read')
        co2_set = setpoints.get('CO2Set')
        if co2_read is not None:
            print(f"  CO2: {co2_read:.1f}ppm (setpoint: {co2_set}ppm)")
        
        # Fan
        fan_read = readings.get('FanRead')
        fan_set = setpoints.get('FanSet')
        if fan_read is not None:
            print(f"  Fan: {fan_read:.0f}rpm (setpoint: {fan_set}%)")


def print_stats(history: dict):
    """Print statistics about the data."""
    data = history.get('data', [])
    
    if not data:
        print("No data available for statistics")
        return
    
    print("\nSTATISTICS:")
    print("-" * 70)
    
    # Collect temperature data
    temps = [entry['readings'].get('Temp1Read') for entry in data 
             if entry.get('readings', {}).get('Temp1Read') is not None]
    
    if temps:
        print(f"Temperature:")
        print(f"  Min: {min(temps):.1f}°C")
        print(f"  Max: {max(temps):.1f}°C")
        print(f"  Avg: {sum(temps)/len(temps):.1f}°C")
    
    # Collect humidity data
    hums = [entry['readings'].get('HumRead') for entry in data 
            if entry.get('readings', {}).get('HumRead') is not None]
    
    if hums:
        print(f"Humidity:")
        print(f"  Min: {min(hums):.1f}%")
        print(f"  Max: {max(hums):.1f}%")
        print(f"  Avg: {sum(hums)/len(hums):.1f}%")
    
    # Count modes
    modes = {}
    for entry in data:
        mode = entry.get('mode', 'Unknown')
        modes[mode] = modes.get(mode, 0) + 1
    
    if modes:
        print(f"Operation Modes:")
        for mode, count in modes.items():
            pct = (count / len(data)) * 100
            print(f"  {mode}: {count} ({pct:.1f}%)")


def print_errors(history: dict):
    """Print any error entries."""
    data = history.get('data', [])
    errors = [entry for entry in data if 'error' in entry]
    
    if not errors:
        print("\n✓ No errors found")
        return
    
    print(f"\n⚠ ERRORS FOUND: {len(errors)}")
    print("-" * 70)
    
    for entry in errors:
        timestamp = entry.get('timestamp', 'Unknown')
        error = entry.get('error', 'Unknown error')
        print(f"[{timestamp}] {error}")


def export_csv(history: dict, output_file: Path):
    """Export data to CSV format."""
    data = history.get('data', [])
    
    if not data:
        print("No data to export")
        return
    
    import csv
    
    # Determine all possible fields
    all_reading_keys = set()
    all_setpoint_keys = set()
    
    for entry in data:
        all_reading_keys.update(entry.get('readings', {}).keys())
        all_setpoint_keys.update(entry.get('setpoints', {}).keys())
    
    # Create header
    header = ['timestamp', 'mode']
    header.extend([f'read_{k}' for k in sorted(all_reading_keys)])
    header.extend([f'set_{k}' for k in sorted(all_setpoint_keys)])
    
    # Write CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        
        for entry in data:
            row = [
                entry.get('timestamp', ''),
                entry.get('mode', '')
            ]
            
            readings = entry.get('readings', {})
            for key in sorted(all_reading_keys):
                row.append(readings.get(key, ''))
            
            setpoints = entry.get('setpoints', {})
            for key in sorted(all_setpoint_keys):
                row.append(setpoints.get(key, ''))
            
            writer.writerow(row)
    
    print(f"✓ Exported {len(data)} entries to {output_file}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='View and analyze Memmert incubator history data'
    )
    parser.add_argument(
        '--log-file',
        type=Path,
        default=Path('data/log/incubator_history.json'),
        help='Path to log file (default: data/log/incubator_history.json)'
    )
    parser.add_argument(
        '--latest',
        type=int,
        metavar='N',
        help='Show latest N entries'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics'
    )
    parser.add_argument(
        '--errors',
        action='store_true',
        help='Show error entries'
    )
    parser.add_argument(
        '--export-csv',
        type=Path,
        metavar='FILE',
        help='Export to CSV file'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Print raw JSON'
    )
    
    args = parser.parse_args()
    
    # Load history
    try:
        history = load_history(args.log_file)
    except Exception as e:
        print(f"Error loading log file: {e}")
        return 1
    
    # Default: show summary
    if not any([args.latest, args.stats, args.errors, args.export_csv, args.json]):
        print_summary(history)
        print_latest(history, 5)
        return 0
    
    # Show summary
    print_summary(history)
    
    # Handle requested actions
    if args.latest:
        print_latest(history, args.latest)
    
    if args.stats:
        print_stats(history)
    
    if args.errors:
        print_errors(history)
    
    if args.export_csv:
        export_csv(history, args.export_csv)
    
    if args.json:
        print("\nRAW JSON:")
        print(json.dumps(history, indent=2))
    
    return 0


if __name__ == '__main__':
    exit(main())
