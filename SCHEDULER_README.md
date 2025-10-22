# Memmert Incubator Scheduler

Automated scheduler for controlling Memmert incubators via AtmoWEB interface using JSON schedule files.

## Features

- ✅ Load setpoint schedules from JSON files
- ✅ Automatic execution at scheduled times
- ✅ Supports Temperature, Humidity, CO2, O2, and Fan setpoints
- ✅ Continuous monitoring or single execution mode
- ✅ Configurable tolerance windows for time-based execution
- ✅ Comprehensive logging and error handling
- ✅ Safe value range validation

## Installation

Make sure you have the required dependencies:

```bash
pip install requests
```

## Quick Start

### 1. Run Continuous Scheduler

Monitor and execute your schedule continuously:

```bash
python memmert_scheduler.py --ip 192.168.100.100 --schedule data/schedules/setpoint_schedule_2025-09-11T08-35-12.json
```

### 2. Run Once (for Cron Jobs)

Execute any currently due setpoints and exit:

```bash
python memmert_scheduler.py --ip 192.168.100.100 --schedule data/schedules/setpoint_schedule_2025-09-11T08-35-12.json --once
```

Add to crontab to run every minute:
```bash
* * * * * cd /home/pi/MemmertControl && python memmert_scheduler.py --once >> logs/scheduler.log 2>&1
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--ip` | `192.168.100.100` | IP address of Memmert device |
| `--schedule` | `data/schedules/setpoint_schedule_2025-09-11T08-35-12.json` | Path to schedule JSON file |
| `--once` | `False` | Run once and exit (for cron) |
| `--duration` | `None` | Run for specified hours |
| `--check-interval` | `30` | Check interval in seconds |
| `--tolerance` | `60` | Time window for execution (seconds) |
| `--verbose` | `False` | Enable debug logging |

## Usage Examples

### Basic Usage

Run the scheduler with default settings:
```bash
python memmert_scheduler.py
```

### Run for 24 Hours

```bash
python memmert_scheduler.py --duration 24
```

### Quick Check Every 10 Seconds

```bash
python memmert_scheduler.py --check-interval 10
```

### Strict Timing (5 second tolerance)

```bash
python memmert_scheduler.py --tolerance 5
```

### Verbose Logging

```bash
python memmert_scheduler.py --verbose
```

### Custom IP and Schedule

```bash
python memmert_scheduler.py \
    --ip 192.168.1.50 \
    --schedule my_custom_schedule.json
```

## Schedule File Format

The scheduler expects JSON files with this structure:

```json
{
  "metadata": {
    "generated": "2025-09-11T08:35:12.133Z",
    "description": "My experiment schedule"
  },
  "schedule": [
    {
      "timestamp": "2025-09-11T10:00:00.000Z",
      "setpoints": {
        "TempSet": 37.0,
        "HumSet": 60.0,
        "CO2Set": 5.0,
        "FanSet": 50
      }
    },
    {
      "timestamp": "2025-09-11T14:00:00.000Z",
      "setpoints": {
        "TempSet": 25.0,
        "HumSet": 40.0
      }
    }
  ]
}
```

### Supported Setpoint Parameters

- `TempSet`: Temperature (°C)
- `HumSet`: Humidity (% RH)
- `CO2Set`: CO2 concentration (%)
- `O2Set`: O2 concentration (%)
- `FanSet`: Fan speed (%)

## How It Works

1. **Load Schedule**: Reads the JSON schedule file
2. **Parse Timestamps**: Converts ISO 8601 timestamps to datetime objects
3. **Monitor Time**: Checks every N seconds (default: 30s) if any setpoint is due
4. **Tolerance Window**: Executes setpoints within ±60 seconds of scheduled time
5. **Apply Setpoints**: Sends commands to incubator via AtmoWEB
6. **Validation**: Checks value ranges before applying
7. **Track Execution**: Marks executed setpoints to prevent duplicate execution

## Logging

The scheduler provides detailed logging:

```
2025-09-11 10:00:15 - INFO - Starting scheduler...
2025-09-11 10:00:15 - INFO - Loaded schedule with 14 setpoints
2025-09-11 10:00:15 - INFO - Next scheduled change in 3585 seconds at 2025-09-11 11:00:00
============================================================
2025-09-11 11:00:05 - INFO - Executing scheduled setpoints at 2025-09-11 11:00:00
============================================================
2025-09-11 11:00:06 - INFO - ✓ Set TempSet=37.0 (actual: 37.0)
2025-09-11 11:00:06 - INFO - ✓ Set HumSet=60.0 (actual: 60.0)
2025-09-11 11:00:07 - INFO - ✓ Set CO2Set=5.0 (actual: 5.0)
2025-09-11 11:00:07 - INFO - Execution summary:
2025-09-11 11:00:07 - INFO -   Success: 3
2025-09-11 11:00:07 - INFO -   Failed: 0
2025-09-11 11:00:07 - INFO -   Not available: 0
```

## Error Handling

The scheduler handles various error conditions:

- **Connection errors**: Logs error and retries on next check
- **Invalid values**: Validates against device ranges before applying
- **Unavailable parameters**: Skips parameters not supported by your device
- **File errors**: Clear error messages for missing/invalid schedule files

## Running as a Service

### Option 1: systemd Service (Linux)

Create `/etc/systemd/system/memmert-scheduler.service`:

```ini
[Unit]
Description=Memmert Incubator Scheduler
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/MemmertControl
ExecStart=/usr/bin/python3 /home/pi/MemmertControl/memmert_scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable memmert-scheduler
sudo systemctl start memmert-scheduler
sudo systemctl status memmert-scheduler
```

### Option 2: Cron (Any Unix/Linux)

Add to crontab for every-minute checks:
```bash
crontab -e
```

Add this line:
```
* * * * * cd /home/pi/MemmertControl && /usr/bin/python3 memmert_scheduler.py --once >> /home/pi/MemmertControl/logs/scheduler.log 2>&1
```

## Troubleshooting

### Connection Refused

```
Failed to connect to device: Connection refused
```

**Solution**: Check that:
1. IP address is correct
2. Ethernet cable is connected
3. Remote Control is enabled on the incubator (see manual section 2.3)

### No Setpoints Executing

**Solution**: Check that:
1. Schedule timestamps are in the future
2. Tolerance window is appropriate (default 60s)
3. Timestamps are in correct timezone

### Parameter Not Available

```
⚠ Parameter CO2Set not available on device
```

**Solution**: This is normal if your device doesn't have that feature (e.g., non-CO2 incubator). The scheduler will skip it and continue.

### Value Out of Range

```
✗ Failed to set TempSet=300: TempSet=300 is outside valid range [0.0, 200.0]
```

**Solution**: Edit your schedule file to use values within your device's supported range.

## Testing

### Test Connection

```bash
python -c "from atmoweb import AtmoWebClient; client = AtmoWebClient('192.168.100.100'); print(client.get_setpoints())"
```

### Test Single Setpoint

```bash
python -c "from atmoweb import AtmoWebClient; client = AtmoWebClient('192.168.100.100'); print(client.set_temperature(25.0))"
```

### Dry Run (Check Schedule Without Executing)

```bash
python memmert_scheduler.py --verbose --once
```

## Tips

- **Start with `--once`** mode to test your schedule before running continuously
- **Use `--verbose`** for debugging
- **Set `--tolerance`** based on your timing requirements (tighter = more precise, but risks missed executions)
- **Check logs regularly** to ensure schedules are executing as expected
- **Test connection** before leaving experiments unattended

## License

Part of the MemmertControl project.
