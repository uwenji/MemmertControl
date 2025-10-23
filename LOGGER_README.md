# Memmert Data Logger

Continuously logs incubator data to a rolling JSON history file and automatically syncs to GitHub.

## Features

✅ Reads current incubator state (readings + setpoints)  
✅ Maintains rolling 3-hour history (configurable)  
✅ Automatically trims old data  
✅ Commits and pushes to GitHub via SSH  
✅ Designed for cron (runs every minute)  
✅ Robust error handling  
✅ Minimal resource usage  

## Quick Start

### 1. Test Connection

```bash
python memmert_logger.py --ip 192.168.100.100 --no-push --verbose
```

This will:
- Read current data
- Save to `data/log/incubator_history.json`
- NOT push to GitHub (test mode)

### 2. Enable GitHub Sync

```bash
python memmert_logger.py --ip 192.168.100.100
```

This will:
- Read current data
- Save to log file
- Commit and push to GitHub

### 3. Setup Cron for Automatic Logging

```bash
# Edit crontab
crontab -e

# Add this line to run every minute:
* * * * * cd /home/pi/MemmertControl && /usr/bin/python3 memmert_logger.py --ip 192.168.100.100 >> logs/logger.log 2>&1
```

## Command Line Options

| Option | Default | Description |
|--------|---------|-------------|
| `--ip` | `192.168.100.100` | IP address of Memmert device |
| `--log-file` | `data/log/incubator_history.json` | Path to log file |
| `--max-hours` | `3.0` | Maximum hours of data to keep |
| `--git-repo` | Auto-detect | Path to git repository |
| `--no-push` | `False` | Disable automatic git push |
| `--verbose` | `False` | Enable debug logging |

## Usage Examples

### Keep 6 Hours of Data

```bash
python memmert_logger.py --max-hours 6.0
```

### Custom Log File Location

```bash
python memmert_logger.py --log-file data/experiment1/history.json
```

### Test Without Git Push

```bash
python memmert_logger.py --no-push
```

### Specify Git Repo Path

```bash
python memmert_logger.py --git-repo /home/pi/MemmertControl
```

## Log File Format

The logger creates a JSON file with this structure:

```json
{
  "metadata": {
    "created": "2025-10-22T10:00:00",
    "device_ip": "192.168.100.100",
    "max_hours": 3.0,
    "last_updated": "2025-10-22T13:00:00",
    "total_entries": 180,
    "time_span_hours": 3.0,
    "description": "Rolling history of Memmert incubator data"
  },
  "data": [
    {
      "timestamp": "2025-10-22T10:00:00",
      "mode": "Manual",
      "readings": {
        "Temp1Read": 25.3,
        "HumRead": 45.2,
        "CO2Read": null,
        "O2Read": null,
        "FanRead": 1250
      },
      "setpoints": {
        "TempSet": 25.0,
        "HumSet": 40.0,
        "CO2Set": null,
        "O2Set": null,
        "FanSet": 50
      }
    },
    {
      "timestamp": "2025-10-22T10:01:00",
      "mode": "Manual",
      "readings": {
        "Temp1Read": 25.2,
        "HumRead": 44.8,
        "FanRead": 1248
      },
      "setpoints": {
        "TempSet": 25.0,
        "HumSet": 40.0,
        "FanSet": 50
      }
    }
  ]
}
```

### Fields Explained

- **metadata**: Information about the log file
  - `created`: When the log was first created
  - `last_updated`: Last update timestamp
  - `total_entries`: Current number of data points
  - `time_span_hours`: Actual time span of data
  
- **data**: Array of measurements (newest last)
  - `timestamp`: When the measurement was taken (ISO 8601)
  - `mode`: Incubator operation mode ("Manual", "Program", "Idle", "Timer")
  - `readings`: Actual sensor values (null if not available)
  - `setpoints`: Target values (null if not available)

## How It Works

### Every Run (Every Minute via Cron)

1. **Read Current Data**
   - Connects to incubator
   - Reads all sensor values (Temp1Read, HumRead, etc.)
   - Reads all setpoints (TempSet, HumSet, etc.)
   - Reads current operation mode

2. **Load History**
   - Opens existing log file
   - Or creates new one if doesn't exist

3. **Append New Data**
   - Adds new entry with timestamp

4. **Trim Old Data**
   - Removes entries older than `max_hours`
   - Keeps only recent data (e.g., last 3 hours)

5. **Save to File**
   - Writes updated JSON
   - Updates metadata

6. **Sync to GitHub**
   - Adds file to git
   - Commits with timestamp
   - Pushes to GitHub

### Data Retention

With default settings (3 hours, 1 minute interval):
- **Maximum entries**: ~180 data points
- **Storage per entry**: ~200-300 bytes
- **Total file size**: ~35-55 KB
- **Git commits**: 1 per minute (GitHub handles this fine)

## Cron Setup

### Basic Setup (Every Minute)

```bash
# Edit crontab
crontab -e

# Add this line:
* * * * * cd /home/pi/MemmertControl && /usr/bin/python3 memmert_logger.py >> logs/logger.log 2>&1
```

### With Custom Settings

```bash
# Keep 6 hours of data
* * * * * cd /home/pi/MemmertControl && /usr/bin/python3 memmert_logger.py --max-hours 6.0 >> logs/logger.log 2>&1
```

### Every 30 Seconds (More Frequent)

```bash
# Run twice per minute
* * * * * cd /home/pi/MemmertControl && /usr/bin/python3 memmert_logger.py >> logs/logger.log 2>&1
* * * * * sleep 30 && cd /home/pi/MemmertControl && /usr/bin/python3 memmert_logger.py >> logs/logger.log 2>&1
```

### Every 5 Minutes (Less Frequent)

```bash
# Run every 5 minutes
*/5 * * * * cd /home/pi/MemmertControl && /usr/bin/python3 memmert_logger.py >> logs/logger.log 2>&1
```

### Create Logs Directory

```bash
mkdir -p /home/pi/MemmertControl/logs
mkdir -p /home/pi/MemmertControl/data/log
```

## GitHub Setup

### Prerequisites

You mentioned you already have SSH setup. Verify it works:

```bash
# Test SSH connection to GitHub
ssh -T git@github.com

# Expected output:
# Hi username! You've successfully authenticated...
```

### First Time Setup

```bash
cd /home/pi/MemmertControl

# Initialize git if not already done
git init

# Add remote (replace with your repo URL)
git remote add origin git@github.com:yourusername/MemmertControl.git

# Or if already exists:
git remote set-url origin git@github.com:yourusername/MemmertControl.git

# Test push
git add .
git commit -m "Initial commit"
git push -u origin main
```

### Verify Auto-Push Works

```bash
# Run logger once
python memmert_logger.py --verbose

# Check git status
git status

# Check recent commits
git log -1

# Check GitHub to see if file appeared
```

## Monitoring

### Check Cron is Running

```bash
# View recent cron logs
grep CRON /var/log/syslog | tail -20

# View logger output
tail -f logs/logger.log
```

### Check Data is Being Collected

```bash
# View log file
cat data/log/incubator_history.json | jq .

# Count entries
jq '.data | length' data/log/incubator_history.json

# View last 5 entries
jq '.data[-5:]' data/log/incubator_history.json

# View latest reading
jq '.data[-1]' data/log/incubator_history.json
```

### Check GitHub Sync

```bash
# View recent commits
git log --oneline -10

# Check if local is ahead/behind remote
git status
```

## Troubleshooting

### Logger Not Running

**Check cron:**
```bash
sudo systemctl status cron
```

**Check crontab:**
```bash
crontab -l
```

**Check permissions:**
```bash
ls -la /home/pi/MemmertControl/memmert_logger.py
chmod +x memmert_logger.py
```

### Connection Errors

```
Failed to connect to device: Connection refused
```

**Solution:**
- Check IP address: `ping 192.168.100.100`
- Verify Remote Control enabled on incubator
- Check ethernet cable

### Git Push Fails

```
Git push failed: Permission denied (publickey)
```

**Solution:**
```bash
# Check SSH key
ls -la ~/.ssh/

# Test GitHub connection
ssh -T git@github.com

# If needed, add key to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519  # or id_rsa
```

### File Permission Errors

```
Permission denied: 'data/log/incubator_history.json'
```

**Solution:**
```bash
# Create directory with correct permissions
mkdir -p data/log
chmod 755 data/log

# Fix file permissions
chmod 644 data/log/incubator_history.json
```

### Disk Space Issues

```bash
# Check disk space
df -h

# Check log file size
du -h data/log/incubator_history.json

# Check git repo size
du -sh .git
```

If git repo gets too large:
```bash
# Reduce max-hours
python memmert_logger.py --max-hours 1.0

# Or compress git history occasionally
git gc --aggressive
```

## Advanced Usage

### Multiple Incubators

Log data from multiple devices:

```bash
# Incubator 1
* * * * * cd /home/pi/MemmertControl && python memmert_logger.py --ip 192.168.100.100 --log-file data/log/incubator1.json

# Incubator 2
* * * * * cd /home/pi/MemmertControl && python memmert_logger.py --ip 192.168.100.101 --log-file data/log/incubator2.json
```

### Backup Logs

```bash
# Daily backup (add to crontab)
0 0 * * * cp /home/pi/MemmertControl/data/log/incubator_history.json /home/pi/backups/history_$(date +\%Y\%m\%d).json
```

### Email Alerts on Errors

```bash
# Install mailutils
sudo apt-get install mailutils

# Modify cron to send errors via email
MAILTO=your@email.com
* * * * * cd /home/pi/MemmertControl && python memmert_logger.py || echo "Logger failed at $(date)" | mail -s "Incubator Logger Error" $MAILTO
```

## Performance

- **CPU Usage**: Minimal (<1% per run)
- **Memory**: ~10-20 MB
- **Disk I/O**: One file write per minute (~50KB)
- **Network**: One git push per minute (~1KB transfer)
- **Git Repo Growth**: ~1.5 MB per day (with 3-hour rolling window)

## Tips

1. **Start with `--no-push`** to test locally first
2. **Use `--verbose`** for debugging
3. **Monitor logs** initially to ensure everything works
4. **Check GitHub** to see commits appearing
5. **Consider git gc** monthly to keep repo size small
6. **Backup important data** before making changes

## Integration with Scheduler

The logger and scheduler work independently:

- **Logger**: Records what IS happening (every minute)
- **Scheduler**: Controls what SHOULD happen (at scheduled times)

Both can run simultaneously via cron.

## Files Created

```
MemmertControl/
├── memmert_logger.py          # The logger script
├── data/
│   └── log/
│       └── incubator_history.json  # Rolling history (auto-created)
└── logs/
    └── logger.log              # Cron output (auto-created)
```

Happy logging! 📊
