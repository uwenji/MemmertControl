# 📊 Memmert Data Logger - Complete Package

## What This Does

The data logger **continuously monitors your incubator** and maintains a rolling history of the last 3 hours (configurable). Every minute, it:

1. ✅ Reads current sensor values (temperature, humidity, etc.)
2. ✅ Reads current setpoints
3. ✅ Saves to a JSON file
4. ✅ Trims data older than 3 hours
5. ✅ Commits and pushes to GitHub automatically

## 📦 Files Included

### Main Scripts (4 files)

1. **memmert_logger.py** (12 KB)
   - Core logging script
   - Reads from incubator
   - Maintains rolling history
   - Pushes to GitHub via SSH

2. **view_history.py** (7 KB)
   - View logged data
   - Show statistics
   - Export to CSV
   - Check for errors

3. **setup_logger_cron.sh** (4 KB)
   - Interactive setup script
   - Configures cron automatically
   - Tests connection and git
   - Makes setup super easy

4. **example_incubator_history.json** (2 KB)
   - Example of what the log file looks like
   - Shows data structure

### Documentation (1 file)

5. **LOGGER_README.md** (15 KB)
   - Complete documentation
   - Setup instructions
   - Troubleshooting guide
   - Advanced usage

## 🚀 Quick Setup (5 Minutes)

### Method 1: Automated Setup (Easiest)

```bash
cd ~/MemmertControl

# Make setup script executable
chmod +x setup_logger_cron.sh

# Run interactive setup
./setup_logger_cron.sh
```

The script will:
- Ask for your incubator IP
- Ask how often to log (every 1/5/10 minutes)
- Test the connection
- Test GitHub SSH
- Add cron job automatically

### Method 2: Manual Setup

```bash
cd ~/MemmertControl

# Create directories
mkdir -p data/log logs

# Test connection (without GitHub push)
python memmert_logger.py --ip 192.168.100.100 --no-push

# If that works, test with GitHub push
python memmert_logger.py --ip 192.168.100.100

# Add to crontab
crontab -e

# Add this line:
* * * * * cd /home/pi/MemmertControl && /usr/bin/python3 memmert_logger.py --ip 192.168.100.100 >> logs/logger.log 2>&1
```

## 📊 View Your Data

### Quick View

```bash
# Show summary and latest 5 entries
python view_history.py

# Show latest 10 entries
python view_history.py --latest 10

# Show statistics
python view_history.py --stats

# Check for errors
python view_history.py --errors
```

### Example Output

```
======================================================================
INCUBATOR HISTORY SUMMARY
======================================================================
Device IP: 192.168.100.100
Created: 2025-10-22T10:00:00
Last Updated: 2025-10-22T13:00:00
Max Hours: 3.0
Total Entries: 180
Time Span: 3.0 hours
First Entry: 2025-10-22T10:00:00
Last Entry: 2025-10-22T13:00:00
======================================================================

LATEST 5 ENTRIES:
----------------------------------------------------------------------

[2025-10-22T12:56:00] Mode: Manual
  Temperature: 25.3°C (setpoint: 25.0°C)
  Humidity: 45.2% (setpoint: 40.0%)
  Fan: 1250rpm (setpoint: 50%)

[2025-10-22T12:57:00] Mode: Manual
  Temperature: 25.2°C (setpoint: 25.0°C)
  Humidity: 44.8% (setpoint: 40.0%)
  Fan: 1248rpm (setpoint: 50%)
...
```

### Export to CSV

```bash
# Export all data to CSV
python view_history.py --export-csv data/incubator_data.csv

# Then analyze in Excel, Python, R, etc.
```

## 📁 Files Created Automatically

After setup and running, your folder will look like:

```
MemmertControl/
├── memmert_logger.py           # Logger script
├── view_history.py              # Data viewer
├── setup_logger_cron.sh         # Setup script
├── LOGGER_README.md             # Documentation
├── data/
│   └── log/
│       └── incubator_history.json   # ← Auto-created by logger
└── logs/
    └── logger.log               # ← Auto-created by cron
```

## 🔄 How It Works

### Every Minute (via Cron)

```
┌─────────────┐
│  Cron Job   │  Triggers every minute
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│  memmert_logger.py  │  Runs the logger
└──────┬──────────────┘
       │
       ├─► Read from Incubator (temperature, humidity, etc.)
       │
       ├─► Load existing history.json
       │
       ├─► Append new data point
       │
       ├─► Trim data older than 3 hours
       │
       ├─► Save to history.json
       │
       └─► Git commit + push to GitHub
```

### Data Retention Example

With default settings (3 hours, 1 minute logging):

```
Time: 10:00 - Data point 1 logged
Time: 10:01 - Data point 2 logged
...
Time: 12:59 - Data point 180 logged
Time: 13:00 - Data point 181 logged
           - Data point 1 (from 10:00) REMOVED (>3 hours old)
Time: 13:01 - Data point 182 logged
           - Data point 2 (from 10:01) REMOVED (>3 hours old)
```

Always keeps last **~180 data points** (3 hours × 60 minutes).

## 🎛️ Configuration Options

### Change Logging Frequency

```bash
# Every 30 seconds (twice per minute)
* * * * * cd /home/pi/MemmertControl && python memmert_logger.py
* * * * * sleep 30 && cd /home/pi/MemmertControl && python memmert_logger.py

# Every 5 minutes
*/5 * * * * cd /home/pi/MemmertControl && python memmert_logger.py

# Every 15 minutes
*/15 * * * * cd /home/pi/MemmertControl && python memmert_logger.py
```

### Change Data Retention

```bash
# Keep 1 hour of data
python memmert_logger.py --max-hours 1.0

# Keep 6 hours of data
python memmert_logger.py --max-hours 6.0

# Keep 24 hours of data
python memmert_logger.py --max-hours 24.0
```

### Disable GitHub Push

```bash
# Log locally only (no GitHub)
python memmert_logger.py --no-push
```

## 📈 Use Cases

### 1. Monitor Experiment Progress

```bash
# Watch data in real-time
watch -n 5 'python view_history.py --latest 3'
```

### 2. Check Temperature Stability

```bash
python view_history.py --stats
```

Output shows min/max/average temperature over the logged period.

### 3. Export for Analysis

```bash
# Export to CSV
python view_history.py --export-csv experiment_data.csv

# Then analyze in Python/R/Excel
```

### 4. Alert on Errors

```bash
# Check for connection errors
python view_history.py --errors

# Or add to cron for email alerts
0 * * * * python view_history.py --errors | mail -s "Incubator Errors" you@email.com
```

### 5. Share Data with Team

Data is automatically on GitHub - your team can:
- Clone the repo to see latest data
- View history file directly on GitHub
- Pull updates to get latest readings

## 🐛 Troubleshooting

### Check if Logger is Running

```bash
# View recent logs
tail -f logs/logger.log

# Check cron jobs
crontab -l

# Check last run time
ls -lh data/log/incubator_history.json
```

### Logger Not Running

```bash
# Test manually
python memmert_logger.py --verbose

# Check cron is running
sudo systemctl status cron

# Check for errors in syslog
grep CRON /var/log/syslog | tail -20
```

### Connection Issues

```bash
# Test connection to incubator
ping 192.168.100.100

# Test with test_connection.py
python test_connection.py 192.168.100.100

# Run logger with verbose output
python memmert_logger.py --verbose --no-push
```

### GitHub Push Failing

```bash
# Test SSH to GitHub
ssh -T git@github.com

# Should see: "Hi username! You've successfully authenticated..."

# If not, check SSH keys
ls -la ~/.ssh/
ssh-add ~/.ssh/id_ed25519  # or id_rsa

# Test manually
cd ~/MemmertControl
git add data/log/incubator_history.json
git commit -m "Test"
git push
```

### Log File Not Updating

```bash
# Check file permissions
ls -la data/log/incubator_history.json

# Check directory permissions
ls -la data/log/

# Fix if needed
chmod 644 data/log/incubator_history.json
chmod 755 data/log/
```

## 📊 Data Format Details

### JSON Structure

```json
{
  "metadata": {
    "created": "When log was first created",
    "device_ip": "Incubator IP address",
    "max_hours": "Max hours of data to keep",
    "last_updated": "Last update timestamp",
    "total_entries": "Number of data points",
    "time_span_hours": "Actual time span of data"
  },
  "data": [
    {
      "timestamp": "ISO 8601 timestamp",
      "mode": "Manual/Program/Idle/Timer",
      "readings": {
        "Temp1Read": "Actual temperature (°C)",
        "HumRead": "Actual humidity (%)",
        "FanRead": "Actual fan speed (rpm)",
        ...
      },
      "setpoints": {
        "TempSet": "Target temperature (°C)",
        "HumSet": "Target humidity (%)",
        "FanSet": "Target fan speed (%)",
        ...
      }
    }
  ]
}
```

### CSV Export Format

When exported to CSV:

```
timestamp,mode,read_Temp1Read,read_HumRead,read_FanRead,set_TempSet,set_HumSet,set_FanSet
2025-10-22T10:00:00,Manual,25.3,45.2,1250,25.0,40.0,50
2025-10-22T10:01:00,Manual,25.2,44.8,1248,25.0,40.0,50
...
```

## 🔗 Integration

### With Scheduler

Both logger and scheduler can run simultaneously:

```bash
# Logger: Records what IS happening (every minute)
* * * * * cd /home/pi/MemmertControl && python memmert_logger.py

# Scheduler: Controls what SHOULD happen (at scheduled times)
* * * * * cd /home/pi/MemmertControl && python memmert_scheduler.py --once
```

### With Monitoring Systems

Export data for use in:
- **Grafana**: Import CSV or read JSON via API
- **Prometheus**: Export metrics
- **Custom dashboards**: Read JSON directly
- **Analysis scripts**: Use Python pandas to load CSV

## 💡 Pro Tips

1. **Start with `--no-push`** to test locally first
2. **Use `--verbose`** when debugging
3. **Check logs regularly** initially: `tail -f logs/logger.log`
4. **Monitor GitHub** to see commits appearing
5. **Export to CSV** for analysis in Excel/Python/R
6. **Backup data** before making changes
7. **Use `view_history.py`** to check data anytime

## 📋 Summary Checklist

Setup checklist:

- [ ] Copy memmert_logger.py to project folder
- [ ] Copy view_history.py to project folder  
- [ ] Copy setup_logger_cron.sh to project folder
- [ ] Make setup script executable: `chmod +x setup_logger_cron.sh`
- [ ] Run setup script: `./setup_logger_cron.sh`
- [ ] Verify cron job: `crontab -l`
- [ ] Wait 1-2 minutes
- [ ] Check log file exists: `ls -lh data/log/incubator_history.json`
- [ ] View data: `python view_history.py`
- [ ] Check GitHub for commits
- [ ] Monitor logs: `tail -f logs/logger.log`

## 🎉 Success Indicators

You'll know everything is working when:

1. **Log file exists**: `data/log/incubator_history.json`
2. **Data is updating**: File timestamp changes every minute
3. **GitHub shows commits**: Check your repo
4. **Logs show success**: `tail logs/logger.log` shows "✓ Logging cycle complete"
5. **View command works**: `python view_history.py` shows data

## 📞 Quick Commands Reference

```bash
# Setup (once)
./setup_logger_cron.sh

# View data
python view_history.py
python view_history.py --latest 10
python view_history.py --stats

# Export data
python view_history.py --export-csv data.csv

# Monitor logs
tail -f logs/logger.log

# Check cron
crontab -l

# Test manually
python memmert_logger.py --verbose --no-push

# Remove cron job
crontab -e  # then delete the line
```

Happy monitoring! 📊🚀
