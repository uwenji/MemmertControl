#!/bin/bash
# Stop all daemon instances completely

echo "🛑 Stopping All Memmert Daemon Instances..."
echo "=============================================="
echo ""

cd ~/Desktop/MemmertControl

# Step 1: Stop systemd service
echo "1. Stopping systemd service..."
if sudo systemctl is-active --quiet memmert-daemon; then
    sudo systemctl stop memmert-daemon
    sleep 2
    
    if sudo systemctl is-active --quiet memmert-daemon; then
        echo "   ⚠️  Service still active, trying force stop..."
        sudo systemctl kill memmert-daemon
        sleep 1
    fi
    echo "   ✓ Systemd service stopped"
else
    echo "   ℹ️  Service was not running"
fi
echo ""

# Step 2: Kill all Python processes
echo "2. Killing all Python daemon processes..."

# Find and kill processes
PIDS=$(pgrep -f "memmert_daemon" 2>/dev/null)

if [ -n "$PIDS" ]; then
    echo "   Found processes: $PIDS"
    
    # Try graceful kill first
    pkill -TERM -f "memmert_daemon" 2>/dev/null
    sleep 2
    
    # Check if still running
    REMAINING=$(pgrep -f "memmert_daemon" 2>/dev/null)
    if [ -n "$REMAINING" ]; then
        echo "   Some processes still running, force killing..."
        pkill -9 -f "memmert_daemon" 2>/dev/null
        sleep 1
    fi
    
    echo "   ✓ All processes terminated"
else
    echo "   ℹ️  No daemon processes found"
fi
echo ""

# Step 3: Final verification
echo "3. Final verification..."

# Check systemd
if sudo systemctl is-active --quiet memmert-daemon; then
    echo "   ✗ ERROR: Service still active!"
    exit 1
else
    echo "   ✓ Service is stopped"
fi

# Check processes
if pgrep -f "memmert_daemon" > /dev/null; then
    echo "   ✗ ERROR: Some processes still running!"
    echo "   Remaining processes:"
    ps aux | grep "[m]emmert_daemon"
    exit 1
else
    echo "   ✓ No daemon processes running"
fi
echo ""

echo "=============================================="
echo "✅ ALL DAEMONS STOPPED"
echo "=============================================="
echo ""
echo "To start the autonomous daemon, run:"
echo "  ./ensure_autonomous_daemon.sh"
echo ""
