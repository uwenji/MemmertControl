# Quick Start Guide - Memmert Scheduler

## 🎯 What You Have

Three Python scripts to control your Memmert incubator:

1. **`memmert_scheduler.py`** - Main scheduler (runs continuously or via cron)
2. **`test_connection.py`** - Test your connection to the incubator  
3. **`apply_schedule_entry.py`** - Manually apply setpoints from schedule (for testing)

## 📋 Prerequisites

```bash
# Install required package
pip install requests

# Your existing files:
# - atmoweb.py (already have)
# - data/schedules/setpoint_schedule_2025-09-11T08-35-12.json (already have)
```

## 🚀 Step-by-Step Setup

### Step 1: Test Your Connection

```bash
cd ~/MemmertControl
python test_connection.py 192.168.100.100
```

**Expected output:**
```
Testing connection to 192.168.100.100...
============================================================
✓ Client created

📊 Current Readings:
  Temp1Read: 28.0
  HumRead: 45.2
  ...

✓ All tests passed!
```

If this fails, check:
- Ethernet cable is connected
- IP address is correct (check on incubator MENU → SETUP)
- Remote Control is enabled on incubator

### Step 2: Test Applying a Single Setpoint

Apply the first entry from your schedule manually:

```bash
python apply_schedule_entry.py data/schedules/setpoint_schedule_2025-09-11T08-35-12.json 0
```

This will:
- Load your schedule file
- Apply the setpoints from entry 0 (first entry)
- Show you what was set

**Expected output:**
```
Loading schedule from: data/schedules/setpoint_schedule_2025-09-11T08-35-12.json

Applying setpoints from entry 0
Scheduled for: 2025-09-11T08:19:45.713Z
Setpoints: {'TempSet': 25, 'HumSet': 40, 'CO2Set': 400, 'FanSet': 50}
------------------------------------------------------------
✓ TempSet=25 (actual: 25.0)
✓ HumSet=40 (actual: 40.0)
⚠ CO2Set=400 - Not available on device
✓ FanSet=50 (actual: 50)
------------------------------------------------------------
Applied 3/4 setpoints successfully
```

### Step 3: Run the Scheduler in Test Mode

Run once to see what it would do:

```bash
python memmert_scheduler.py --once --verbose
```

This will:
- Load your schedule
- Check if any setpoints are due NOW
- Execute them if within time window
- Exit

### Step 4: Run the Scheduler Continuously

Let it run and monitor your schedule:

```bash
python memmert_scheduler.py
```

**Expected output:**
```
2025-10-22 10:00:15 - INFO - Starting scheduler...
2025-10-22 10:00:15 - INFO - Check interval: 30 seconds
2025-10-22 10:00:15 - INFO - Loaded schedule with 14 setpoints
2025-10-22 10:00:15 - INFO - Next scheduled change in 3585 seconds at 2025-09-11 11:00:00
```

Press Ctrl+C to stop.

## 📝 Common Commands

### Run for 24 hours
```bash
python memmert_scheduler.py --duration 24
```

### Check every 10 seconds (more responsive)
```bash
python memmert_scheduler.py --check-interval 10
```

### Use different IP
```bash
python memmert_scheduler.py --ip 192.168.1.50
```

### Use different schedule file
```bash
python memmert_scheduler.py --schedule my_experiment.json
```

### Save logs to file
```bash
python memmert_scheduler.py > logs/scheduler.log 2>&1
```

## 🔧 Setup as Background Service

### Option 1: Screen Session (Simple)

```bash
# Start in background
screen -S memmert
python memmert_scheduler.py

# Detach: Press Ctrl+A then D

# Reattach later
screen -r memmert

# Kill session
screen -X -S memmert quit
```

### Option 2: Cron Job (Runs every minute)

```bash
# Edit crontab
crontab -e

# Add this line:
* * * * * cd /home/pi/MemmertControl && /usr/bin/python3 memmert_scheduler.py --once >> /home/pi/MemmertControl/logs/scheduler.log 2>&1

# Create logs directory
mkdir -p logs
```

### Option 3: systemd Service (Most robust)

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

Then:
```bash
sudo systemctl enable memmert-scheduler
sudo systemctl start memmert-scheduler
sudo systemctl status memmert-scheduler

# View logs
sudo journalctl -u memmert-scheduler -f
```

## 🐛 Troubleshooting

### "Connection refused"
- Check Remote Control is enabled on incubator (MENU → SETUP → Remote Control → Read/Write)
- Verify IP: `ping 192.168.100.100`

### "No setpoints due now"
- Check your schedule timestamps are in the future
- Increase tolerance: `--tolerance 300` (5 minutes)

### "Parameter not available"
- Normal if your device doesn't have that feature (e.g., CO2 on non-CO2 model)
- The scheduler will skip it

### Check current incubator state
```bash
curl http://192.168.100.100/atmoweb?Temp1Read=\&TempSet=
```

## 📊 Monitoring

### View what's scheduled next
The scheduler logs this automatically:
```
Next scheduled change in 3585 seconds at 2025-09-11 11:00:00
```

### Check if scheduler is running
```bash
# If using screen:
screen -ls

# If using systemd:
sudo systemctl status memmert-scheduler

# If using cron, check logs:
tail -f logs/scheduler.log
```

## 🎯 Your Schedule File

Your schedule sets all parameters to:
- Temperature: 25°C
- Humidity: 40% RH
- CO2: 400 ppm
- Fan: 50%

At 14 different times over 20 hours (from your JSON).

To modify:
1. Edit `data/schedules/setpoint_schedule_2025-09-11T08-35-12.json`
2. Update timestamps and setpoints
3. Restart the scheduler

## 💡 Tips

1. **Test first**: Always run `--once` mode first to verify
2. **Use verbose**: Add `--verbose` when debugging
3. **Save logs**: Redirect output to a log file
4. **Monitor initially**: Watch the first few executions to ensure it works
5. **Network stability**: Use ethernet (not WiFi) for reliable connection

## 📞 Need Help?

Check:
- `SCHEDULER_README.md` - Full documentation
- Memmert manual (already uploaded) - Section 4 "Using AtmoWEB commands"
- Connection test: `python test_connection.py`

Happy scheduling! 🚀
