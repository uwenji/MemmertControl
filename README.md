# 🔬 Complete Memmert Incubator Control System

Your complete automation solution for Memmert incubators with REST API control and data logging.

## 📦 What You Have

### Two Independent Systems

#### 1. 📅 **Scheduler** - Automated Control
Controls your incubator based on JSON schedules. Sets temperature, humidity, CO2, etc. at scheduled times.

#### 2. 📊 **Logger** - Data Recording  
Continuously monitors and records incubator data. Maintains rolling 3-hour history and syncs to GitHub.

**Both work independently and can run simultaneously!**

---

## 🗂️ All Files (13 total)

### Scheduler Files (7 files)

| File | Size | Purpose |
|------|------|---------|
| `memmert_scheduler.py` | 14 KB | Main scheduler - executes setpoint schedules |
| `apply_schedule_entry.py` | 3.4 KB | Manually apply specific schedule entries |
| `create_schedule_example.py` | 11 KB | Generate custom schedules programmatically |
| `test_connection.py` | 2 KB | Test incubator connection |
| `SCHEDULER_README.md` | 7.2 KB | Scheduler documentation |
| `QUICK_START.md` | 5.9 KB | Quick start guide for scheduler |
| `FILES_OVERVIEW.md` | 7.5 KB | Overview of all files |

**Start Here for Scheduler:** [QUICK_START.md](computer:///mnt/user-data/outputs/QUICK_START.md)

### Logger Files (6 files)

| File | Size | Purpose |
|------|------|---------|
| `memmert_logger.py` | 13 KB | Main logger - records data every minute |
| `view_history.py` | 7.7 KB | View and analyze logged data |
| `setup_logger_cron.sh` | 5.5 KB | Interactive setup for cron job |
| `example_incubator_history.json` | 2.6 KB | Example log file format |
| `LOGGER_README.md` | 9.9 KB | Logger documentation |
| `LOGGER_SUMMARY.md` | 12 KB | Logger quick start guide |

**Start Here for Logger:** [LOGGER_SUMMARY.md](computer:///mnt/user-data/outputs/LOGGER_SUMMARY.md)

---

## 🚀 Super Quick Start

### 1. Setup Scheduler (5 minutes)

```bash
cd ~/MemmertControl

# Test connection
python test_connection.py 192.168.100.100

# Run your schedule
python memmert_scheduler.py --schedule data/schedules/setpoint_schedule.json
```

### 2. Setup Logger (5 minutes)

```bash
# Make setup script executable
chmod +x setup_logger_cron.sh

# Run interactive setup
./setup_logger_cron.sh
```

That's it! Your incubator is now:
- ✅ Running scheduled experiments
- ✅ Logging data every minute
- ✅ Syncing to GitHub automatically

---

## 🎯 Common Use Cases

### Use Case 1: Scheduled Experiment with Data Logging

**Goal**: Run a temperature ramp experiment and log all data

```bash
# 1. Start the logger (via cron - already setup)
#    This runs automatically every minute

# 2. Start the scheduler with your experiment schedule
python memmert_scheduler.py --schedule data/schedules/my_experiment.json

# 3. Monitor in real-time
tail -f logs/logger.log        # Watch logger
watch 'python view_history.py --latest 3'  # Watch data
```

### Use Case 2: Manual Control with Data Recording

**Goal**: Manually set conditions and record data

```bash
# 1. Logger is already running (via cron)

# 2. Manually set conditions
python -c "from archive.atmoweb import AtmoWebClient; \
           client = AtmoWebClient('192.168.100.100'); \
           client.set_temperature(37.0); \
           client.set_humidity(60.0)"

# 3. View recorded data
python view_history.py
```

### Use Case 3: Long-Term Monitoring Only

**Goal**: Just log data without scheduled control

```bash
# Logger is already running via cron
# Just check data periodically
python view_history.py --stats

# Export for analysis
python view_history.py --export-csv experiment_data.csv
```

### Use Case 4: One-Time Setpoint Application

**Goal**: Apply specific setpoints from schedule once

```bash
# Apply first entry from your schedule
python apply_schedule_entry.py data/schedules/setpoint_schedule.json 0

# Logger continues recording in background
```

---

## 📊 Complete Workflow Example

Here's a complete workflow from start to finish:

### Day 1: Setup

```bash
cd ~/MemmertControl

# 1. Test connection
python test_connection.py 192.168.100.100
# ✓ Connected

# 2. Setup data logger (once)
./setup_logger_cron.sh
# ✓ Logger will run every minute

# 3. Create your experiment schedule
python create_schedule_example.py
# Creates example schedules in data/schedules/

# 4. Verify everything works
python view_history.py
# Shows data is being logged
```

### Day 2: Run Experiment

```bash
# Start your scheduled experiment
python memmert_scheduler.py --schedule data/schedules/ramp_schedule.json --duration 24

# In another terminal, monitor progress
watch -n 10 'python view_history.py --latest 1'
```

### Day 3: Analyze Results

```bash
# Export data
python view_history.py --export-csv results.csv

# View statistics
python view_history.py --stats

# Check for any errors
python view_history.py --errors
```

---

## 📁 Your Project Structure

After setup, your folder should look like:

```
MemmertControl/
├── archive/                        # Your existing files
│   ├── atmoweb.py                  # (keep this - others import it)
│   └── ...
│
├── data/
│   ├── schedules/
│   │   └── setpoint_schedule.json  # Your schedules
│   └── log/
│       └── incubator_history.json  # Auto-created by logger
│
├── logs/
│   └── logger.log                  # Cron output
│
├── memmert_scheduler.py            # Scheduler
├── memmert_logger.py               # Logger
├── apply_schedule_entry.py         # Manual control
├── test_connection.py              # Connection tester
├── view_history.py                 # Data viewer
├── create_schedule_example.py      # Schedule generator
├── setup_logger_cron.sh            # Logger setup
│
├── QUICK_START.md                  # Start here for scheduler
├── LOGGER_SUMMARY.md               # Start here for logger
├── SCHEDULER_README.md             # Full scheduler docs
├── LOGGER_README.md                # Full logger docs
└── FILES_OVERVIEW.md               # This file
```

---

## 🔧 Scheduler vs Logger

### When to Use What

| Feature | Scheduler | Logger |
|---------|-----------|--------|
| **Purpose** | Control incubator | Record data |
| **Runs** | Scheduled/Continuous | Every minute (cron) |
| **Reads** | Schedule JSON files | Incubator sensors |
| **Writes** | Sets incubator parameters | Saves to history JSON |
| **GitHub** | No | Yes (auto-push) |

### They Work Together

```
Scheduler                    Logger
    │                          │
    ├─► Sets TempSet=37°C     │
    │                          │
    │                          ├─► Reads Temp1Read=25.1°C
    │                          ├─► Reads TempSet=37.0°C
    │                          ├─► Saves to history.json
    │                          └─► Pushes to GitHub
    │                          
    ├─► (incubator heating)   │
    │                          │
    │                          ├─► Reads Temp1Read=30.5°C
    │                          ├─► Saves to history.json
    │                          └─► Pushes to GitHub
    │
    └─► Sets HumSet=60%        │
                               │
                               ├─► Reads Temp1Read=37.0°C
                               ├─► Reads HumRead=45.2%
                               ├─► Saves to history.json
                               └─► Pushes to GitHub
```

---

## 🐛 Troubleshooting Quick Reference

### Connection Issues

```bash
# Test ping
ping 192.168.100.100

# Test connection
python test_connection.py 192.168.100.100

# Check Remote Control enabled on incubator
# Menu → Setup → Remote Control → Write
```

### Scheduler Not Working

```bash
# Test manually
python memmert_scheduler.py --once --verbose

# Check schedule file
cat data/schedules/setpoint_schedule.json | jq .

# Check timestamps are in future
```

### Logger Not Running

```bash
# Check cron
crontab -l

# View logs
tail -f logs/logger.log

# Test manually
python memmert_logger.py --verbose --no-push
```

### GitHub Not Syncing

```bash
# Test SSH
ssh -T git@github.com

# Check git status
git status
git log -3

# Manual push
git push
```

---

## 📖 Documentation Guide

### For Quick Setup
1. **QUICK_START.md** - Scheduler setup in 5 minutes
2. **LOGGER_SUMMARY.md** - Logger setup in 5 minutes

### For Complete Reference
1. **SCHEDULER_README.md** - Full scheduler documentation
2. **LOGGER_README.md** - Full logger documentation

### For Understanding
1. **FILES_OVERVIEW.md** - What each file does
2. **This file** - How everything fits together

---

## 💡 Pro Tips

1. **Test connection first**: Always run `test_connection.py` before anything else
2. **Start with `--once`**: Test scheduler with `--once` flag first
3. **Start with `--no-push`**: Test logger without GitHub first
4. **Monitor initially**: Watch logs for first few hours
5. **Use `--verbose`**: Add when debugging any issues
6. **Check GitHub**: Verify commits appearing
7. **Export data**: Use `view_history.py --export-csv` for analysis
8. **Backup schedules**: Keep copies of important schedule files

---

## ⚙️ Advanced Configuration

### Run Both with Cron

```bash
crontab -e

# Logger: Every minute
* * * * * cd /home/pi/MemmertControl && python memmert_logger.py >> logs/logger.log 2>&1

# Scheduler: Check for scheduled changes every minute
* * * * * cd /home/pi/MemmertControl && python memmert_scheduler.py --once >> logs/scheduler.log 2>&1
```

### Multiple Incubators

```bash
# Incubator 1
* * * * * cd /home/pi/MemmertControl && python memmert_logger.py --ip 192.168.100.100 --log-file data/log/incubator1.json

# Incubator 2
* * * * * cd /home/pi/MemmertControl && python memmert_logger.py --ip 192.168.100.101 --log-file data/log/incubator2.json
```

### Different Data Retention

```bash
# Short term (1 hour)
python memmert_logger.py --max-hours 1.0

# Long term (24 hours)
python memmert_logger.py --max-hours 24.0
```

---

## 📞 Quick Command Reference

### Scheduler Commands
```bash
# Test connection
python test_connection.py 192.168.100.100

# Run schedule continuously
python memmert_scheduler.py --schedule data/schedules/setpoint_schedule.json

# Run once (for cron)
python memmert_scheduler.py --once

# Apply single entry
python apply_schedule_entry.py data/schedules/setpoint_schedule.json 0
```

### Logger Commands
```bash
# Setup (once)
./setup_logger_cron.sh

# Test manually
python memmert_logger.py --verbose --no-push

# View data
python view_history.py
python view_history.py --latest 10
python view_history.py --stats

# Export
python view_history.py --export-csv data.csv
```

### Monitoring Commands
```bash
# Watch logs
tail -f logs/logger.log
tail -f logs/scheduler.log

# Check cron
crontab -l

# View data in real-time
watch -n 5 'python view_history.py --latest 3'

# Check GitHub
git log --oneline -10
git status
```

---

## ✅ Setup Checklist

Complete setup checklist for both systems:

### Initial Setup
- [ ] Test incubator connection
- [ ] Verify Remote Control enabled on incubator
- [ ] Test GitHub SSH access

### Scheduler Setup
- [ ] Copy scheduler files to project
- [ ] Test with `--once` flag
- [ ] Create/verify schedule files
- [ ] Setup cron if needed

### Logger Setup
- [ ] Copy logger files to project
- [ ] Run `setup_logger_cron.sh`
- [ ] Verify cron job created
- [ ] Check data file being created
- [ ] Verify GitHub commits appearing

### Verification
- [ ] Wait 5-10 minutes
- [ ] Check `data/log/incubator_history.json` exists
- [ ] Run `python view_history.py`
- [ ] Check GitHub for commits
- [ ] Verify scheduler executing setpoints (if running)

---

## 🎉 You're All Set!

You now have a complete system for:
- ✅ Automated incubator control via schedules
- ✅ Continuous data logging
- ✅ Automatic GitHub backup
- ✅ Real-time monitoring
- ✅ Data export and analysis

**Next Steps:**
1. Read QUICK_START.md for scheduler
2. Read LOGGER_SUMMARY.md for logger
3. Run both systems
4. Monitor your experiments!

Happy automating! 🔬🚀

---

**Questions?** Check the detailed README files for each system.

**Issues?** See the Troubleshooting sections in the documentation.

**Need help?** All scripts support `--help` flag for options.
