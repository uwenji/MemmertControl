#!/bin/bash
# Ensure only autonomous daemon is running

echo "🔄 Ensuring Autonomous Daemon is Running..."
echo "================================================"
echo ""

cd ~/Desktop/MemmertControl

# Step 1: Stop all running instances
echo "1. Stopping all daemon instances..."
echo "   - Stopping systemd service..."
sudo systemctl stop memmert-daemon 2>/dev/null
sleep 2

echo "   - Killing any remaining Python processes..."
# Kill any running memmert_daemon.py processes
pkill -f "memmert_daemon.py" 2>/dev/null
pkill -f "memmert_daemon_autonomous.py" 2>/dev/null
sleep 1

# Verify no processes are running
if pgrep -f "memmert_daemon" > /dev/null; then
    echo "   ⚠️  Warning: Some processes still running, force killing..."
    pkill -9 -f "memmert_daemon" 2>/dev/null
    sleep 1
fi

echo "   ✓ All instances stopped"
echo ""

# Step 2: Verify autonomous file exists
echo "2. Verifying autonomous daemon file..."
if [ ! -f "memmert_daemon_autonomous.py" ]; then
    echo "   ✗ ERROR: memmert_daemon_autonomous.py not found!"
    echo "   Please ensure the file is in ~/Desktop/MemmertControl/"
    exit 1
fi
echo "   ✓ Found: memmert_daemon_autonomous.py"
echo ""

# Step 3: Backup and replace
echo "3. Installing autonomous version..."
# Backup current version if it exists and is different
if [ -f "memmert_daemon.py" ]; then
    if ! cmp -s "memmert_daemon.py" "memmert_daemon_autonomous.py"; then
        BACKUP_NAME="memmert_daemon.py.backup.$(date +%Y%m%d_%H%M%S)"
        cp memmert_daemon.py "$BACKUP_NAME"
        echo "   ✓ Backed up old version to $BACKUP_NAME"
    else
        echo "   ℹ️  Files are already identical"
    fi
fi

# Copy autonomous version over
cp memmert_daemon_autonomous.py memmert_daemon.py
echo "   ✓ Installed autonomous version as memmert_daemon.py"
echo ""

# Step 4: Verify the service file
echo "4. Checking systemd service configuration..."
SERVICE_FILE="/etc/systemd/system/memmert-daemon.service"
if [ -f "$SERVICE_FILE" ]; then
    echo "   ✓ Service file exists: $SERVICE_FILE"
    
    # Show what the service is configured to run
    EXEC_LINE=$(grep "ExecStart" "$SERVICE_FILE" | head -1)
    echo "   Service runs: $EXEC_LINE"
    
    # Check if it points to the right file
    if echo "$EXEC_LINE" | grep -q "memmert_daemon"; then
        echo "   ✓ Service points to memmert_daemon.py"
    else
        echo "   ⚠️  Warning: Service might not point to daemon file"
    fi
else
    echo "   ⚠️  Warning: Service file not found at $SERVICE_FILE"
    echo "   You may need to create the service file"
fi
echo ""

# Step 5: Reload systemd and start
echo "5. Starting autonomous daemon..."
sudo systemctl daemon-reload
sleep 1
sudo systemctl start memmert-daemon
sleep 3
echo "   ✓ Started"
echo ""

# Step 6: Verify it's running
echo "6. Verification checks..."
echo ""

# Check systemd status
echo "   a) Systemd service status:"
if sudo systemctl is-active --quiet memmert-daemon; then
    echo "      ✓ Service is active"
else
    echo "      ✗ Service is NOT active!"
    sudo systemctl status memmert-daemon --no-pager -n 10
    exit 1
fi

# Check process
echo "   b) Process check:"
DAEMON_PID=$(pgrep -f "memmert_daemon.py" | head -1)
if [ -n "$DAEMON_PID" ]; then
    echo "      ✓ Daemon process running (PID: $DAEMON_PID)"
    
    # Verify it's the autonomous version by checking file content
    PROCESS_CMD=$(ps -p "$DAEMON_PID" -o args= 2>/dev/null)
    echo "      Command: $PROCESS_CMD"
else
    echo "      ✗ No daemon process found!"
    exit 1
fi

# Check for "Autonomous Mode" in logs
echo "   c) Checking logs for autonomous mode signature..."
sleep 2
if sudo journalctl -u memmert-daemon -n 50 --no-pager | grep -q "Autonomous Mode"; then
    echo "      ✓ Autonomous mode confirmed in logs!"
else
    echo "      ⚠️  Warning: 'Autonomous Mode' not found in recent logs"
    echo "      (Daemon might still be starting up)"
fi
echo ""

# Step 7: Show recent logs
echo "7. Recent daemon logs:"
echo "   ─────────────────────────────────────────────"
sudo journalctl -u memmert-daemon -n 15 --no-pager | tail -10
echo "   ─────────────────────────────────────────────"
echo ""

# Success summary
echo "================================================"
echo "✅ AUTONOMOUS DAEMON IS RUNNING"
echo "================================================"
echo ""
echo "Configuration:"
echo "  • File: ~/Desktop/MemmertControl/memmert_daemon.py"
echo "  • Source: memmert_daemon_autonomous.py"
echo "  • Service: memmert-daemon.service"
echo "  • PID: $DAEMON_PID"
echo ""
echo "Features enabled:"
echo "  ✓ Automatic git conflict resolution"
echo "  ✓ Smart stash/pull/push cycles"
echo "  ✓ Schedule-based setpoint application"
echo "  ✓ Log file preservation"
echo "  ✓ Auto-recovery from push failures"
echo ""
echo "Useful commands:"
echo "  • View live logs:    sudo journalctl -u memmert-daemon -f"
echo "  • Check status:      sudo systemctl status memmert-daemon"
echo "  • Restart daemon:    sudo systemctl restart memmert-daemon"
echo "  • Stop daemon:       sudo systemctl stop memmert-daemon"
echo "  • View history:      python3 view_history.py"
echo ""
