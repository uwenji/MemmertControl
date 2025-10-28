#!/bin/bash
# Update to fully autonomous daemon

echo "🔄 Updating to Autonomous Daemon..."
echo ""

cd ~/Desktop/MemmertControl

# Stop daemon
echo "1. Stopping daemon..."
sudo systemctl stop memmert-daemon
sleep 2
echo "✓ Stopped"
echo ""

# Backup old version
echo "2. Backing up old version..."
if [ -f "memmert_daemon.py" ]; then
    cp memmert_daemon.py memmert_daemon.py.old
    echo "✓ Backed up to memmert_daemon.py.old"
else
    echo "  (No old version found)"
fi
echo ""

# Copy new version
echo "3. Installing autonomous version..."
if [ -f "memmert_daemon_autonomous.py" ]; then
    cp memmert_daemon_autonomous.py memmert_daemon.py
    echo "✓ Installed"
else
    echo "✗ memmert_daemon_autonomous.py not found!"
    echo "  Please download it first"
    exit 1
fi
echo ""

# Start daemon
echo "4. Starting daemon..."
sudo systemctl start memmert-daemon
sleep 3
echo "✓ Started"
echo ""

# Show status
echo "5. Status:"
sudo systemctl status memmert-daemon --no-pager -n 5
echo ""

echo "🎉 Update complete!"
echo ""
echo "The new daemon will automatically:"
echo "  ✓ Handle all git conflicts"
echo "  ✓ Stash changes before pulling"
echo "  ✓ Reset to clean state if needed"
echo "  ✓ Preserve log file through all operations"
echo "  ✓ Retry push with smart recovery"
echo ""
echo "Monitor: sudo journalctl -u memmert-daemon -f"
echo ""
