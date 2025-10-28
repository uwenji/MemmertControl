#!/bin/bash
# Fix git state and restart daemon

echo "🔧 Fixing git state and restarting daemon..."
echo ""

# Stop daemon
echo "1. Stopping daemon..."
sudo systemctl stop memmert-daemon
echo "✓ Stopped"
echo ""

# Fix git
cd ~/Desktop/MemmertControl

echo "2. Fixing git repository..."
git stash
echo "✓ Stashed changes"

git pull --rebase
echo "✓ Pulled from GitHub"

git stash pop 2>/dev/null || echo "  (No changes to pop)"
echo "✓ Git state fixed"
echo ""

# Update daemon with improved version
echo "3. Updating daemon..."
if [ -f "memmert_daemon.py.new" ]; then
    cp memmert_daemon.py.new memmert_daemon.py
    echo "✓ Daemon updated with auto-stash feature"
else
    echo "  (Using existing daemon)"
fi
echo ""

# Restart daemon
echo "4. Restarting daemon..."
sudo systemctl start memmert-daemon
echo "✓ Daemon restarted"
echo ""

# Show status
echo "5. Checking status..."
sleep 2
sudo systemctl status memmert-daemon --no-pager -n 10
echo ""

echo "🎉 Done!"
echo ""
echo "Monitor with: sudo journalctl -u memmert-daemon -f"
echo ""
