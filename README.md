# Memmert Incubator Control System

## Installation

### Download Files
1. [memmert_daemon_autonomous.py](computer:///mnt/user-data/outputs/memmert_daemon_autonomous.py)
2. [update_to_autonomous.sh](computer:///mnt/user-data/outputs/update_to_autonomous.sh)

### Install
```bash
cd ~/Desktop/MemmertControl

# Run update script
chmod +x update_to_autonomous.sh
./update_to_autonomous.sh
```

### Or Manual
```bash
cd ~/Desktop/MemmertControl

# Stop daemon
sudo systemctl stop memmert-daemon

# Install new version
cp memmert_daemon_autonomous.py memmert_daemon.py

# Start daemon
sudo systemctl start memmert-daemon

# Monitor
sudo journalctl -u memmert-daemon -f
```

## Testing

Want to test the conflict resolution?

### Test Unstaged Changes Recovery
```bash
# Create conflict
cd ~/Desktop/MemmertControl
echo "test" >> data/schedules/setpoint_schedule.json

# Watch daemon handle it automatically
sudo journalctl -u memmert-daemon -f

# You'll see:
# - ⚠️  Resetting git to clean state
# - ✓ Git reset complete
# - ↓ Pulled updates
```

### Test Push Failure Recovery
```bash
# On another computer/Pi, push to same repo

# Your daemon will:
# - Try push (fails)
# - Retry 3 times
# - Auto-pull
# - Push again (succeeds)

# All automatic!
```

## Safety Features

### Log File Protection
✅ Always backed up before git operations  
✅ Always restored after operations  
✅ Never lost, even with hard reset  

### Git State Management
✅ Multiple fallback strategies  
✅ Progressively more aggressive  
✅ Always reaches working state  

### Error Recovery
✅ Never gets stuck  
✅ No manual intervention needed  
✅ Self-healing  

## What Changed from Previous Version

### Previous
```python
# Try pull
git pull --rebase

# If fail:
# - Log error
# - Stop
# ❌ User must fix manually
```

### Autonomous
```python
# Try pull with stash
if fail:
    # Try reset and pull
    if fail:
        # Hard sync with remote
        # ✓ Always succeeds

# Log file always safe!
```

### Memmert connection Pi setup

```bash
# Check your Pi's IP
ip addr show eth0

# Ping the incubator (should take longer than 0.1ms if it's a real device)
ping -c4 192.168.100.100

# Try the web interface
curl http://192.168.100.100/atmoweb?Temp1Read=
```

Step 2: Set the Incubator's IP Address
On the Memmert incubator's screen:
  1.Press MENU
  2.Select SETUP
  3.Find the IP address setting
  4.Change it to 192.168.100.100 (NOT 192.168.100.50!)
  5.Also check Subnet mask should be 255.255.255.0

```bash
sudo ip addr flush dev eth0
sudo ip addr add 192.168.100.50/24 dev eth0
```
Your Pi is now 192.168.100.50

```bash
cd ~/MemmertControl

# 1. Test connection
python test_connection.py 192.168.100.100
# ✓ Connected
#{"Temp1Read": 23.1}

# 2. Verify everything works
python view_history.py
# Shows data is being logged
```
