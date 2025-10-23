#!/bin/bash
# Setup script for Memmert Data Logger cron job

set -e

echo "========================================"
echo "Memmert Data Logger - Cron Setup"
echo "========================================"
echo ""

# Get current directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_PATH=$(which python3)

echo "Project directory: $SCRIPT_DIR"
echo "Python path: $PYTHON_PATH"
echo ""

# Default values
DEFAULT_IP="192.168.100.100"
DEFAULT_INTERVAL="1"  # minutes

# Ask for IP
read -p "Enter incubator IP address [$DEFAULT_IP]: " IP
IP=${IP:-$DEFAULT_IP}

# Ask for interval
echo ""
echo "How often should data be logged?"
echo "  1) Every minute (recommended)"
echo "  2) Every 5 minutes"
echo "  3) Every 10 minutes"
echo "  4) Custom interval"
read -p "Choose [1-4]: " INTERVAL_CHOICE

case $INTERVAL_CHOICE in
    1)
        CRON_SCHEDULE="* * * * *"
        INTERVAL_DESC="every minute"
        ;;
    2)
        CRON_SCHEDULE="*/5 * * * *"
        INTERVAL_DESC="every 5 minutes"
        ;;
    3)
        CRON_SCHEDULE="*/10 * * * *"
        INTERVAL_DESC="every 10 minutes"
        ;;
    4)
        read -p "Enter cron schedule (e.g., '*/2 * * * *' for every 2 minutes): " CRON_SCHEDULE
        INTERVAL_DESC="custom schedule"
        ;;
    *)
        CRON_SCHEDULE="* * * * *"
        INTERVAL_DESC="every minute"
        ;;
esac

# Ask for max hours
read -p "Maximum hours of data to keep [3.0]: " MAX_HOURS
MAX_HOURS=${MAX_HOURS:-3.0}

# Create directories
echo ""
echo "Creating directories..."
mkdir -p "$SCRIPT_DIR/data/log"
mkdir -p "$SCRIPT_DIR/logs"
echo "✓ Directories created"

# Test connection
echo ""
echo "Testing connection to incubator..."
if $PYTHON_PATH "$SCRIPT_DIR/memmert_logger.py" --ip "$IP" --no-push --verbose 2>&1 | grep -q "Logging cycle complete"; then
    echo "✓ Connection test successful"
else
    echo "⚠ Connection test failed. Please check:"
    echo "  - IP address is correct"
    echo "  - Incubator is powered on and connected"
    echo "  - Remote Control is enabled on incubator"
    read -p "Continue anyway? [y/N]: " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled"
        exit 1
    fi
fi

# Test Git
echo ""
echo "Testing Git configuration..."
cd "$SCRIPT_DIR"
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo "✓ Git repository detected"
    
    # Test Git SSH
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "✓ GitHub SSH authentication working"
    else
        echo "⚠ GitHub SSH authentication not working"
        echo "  You may need to setup SSH keys for GitHub"
        read -p "Disable auto-push to GitHub? [y/N]: " DISABLE_PUSH
        if [[ "$DISABLE_PUSH" =~ ^[Yy]$ ]]; then
            NO_PUSH="--no-push"
        else
            NO_PUSH=""
        fi
    fi
else
    echo "⚠ Not a git repository"
    read -p "Disable auto-push to GitHub? [y/N]: " DISABLE_PUSH
    if [[ "$DISABLE_PUSH" =~ ^[Yy]$ ]]; then
        NO_PUSH="--no-push"
    else
        NO_PUSH=""
    fi
fi

# Build cron command
CRON_CMD="cd $SCRIPT_DIR && $PYTHON_PATH $SCRIPT_DIR/memmert_logger.py --ip $IP --max-hours $MAX_HOURS $NO_PUSH >> $SCRIPT_DIR/logs/logger.log 2>&1"

# Show cron entry
echo ""
echo "========================================"
echo "Cron job configuration:"
echo "========================================"
echo "Schedule: $CRON_SCHEDULE ($INTERVAL_DESC)"
echo "Command: $CRON_CMD"
echo ""

# Ask to install
read -p "Add this cron job? [y/N]: " ADD_CRON
if [[ ! "$ADD_CRON" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Cron job not added. To add it manually:"
    echo "1. Run: crontab -e"
    echo "2. Add this line:"
    echo ""
    echo "$CRON_SCHEDULE $CRON_CMD"
    echo ""
    exit 0
fi

# Add to crontab
echo ""
echo "Adding cron job..."

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "memmert_logger.py"; then
    echo "⚠ A memmert_logger cron job already exists"
    read -p "Replace it? [y/N]: " REPLACE
    if [[ "$REPLACE" =~ ^[Yy]$ ]]; then
        # Remove old job
        crontab -l 2>/dev/null | grep -v "memmert_logger.py" | crontab -
        echo "Old cron job removed"
    else
        echo "Keeping existing cron job"
        exit 0
    fi
fi

# Add new job
(crontab -l 2>/dev/null; echo "$CRON_SCHEDULE $CRON_CMD") | crontab -
echo "✓ Cron job added"

# Verify
echo ""
echo "Verifying cron job..."
if crontab -l | grep -q "memmert_logger.py"; then
    echo "✓ Cron job verified"
else
    echo "⚠ Could not verify cron job"
fi

# Show current crontab
echo ""
echo "Current crontab:"
echo "----------------------------------------"
crontab -l | grep "memmert_logger.py" || echo "(none found)"
echo "----------------------------------------"

# Done
echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "The logger will run $INTERVAL_DESC and:"
echo "  - Read data from incubator at $IP"
echo "  - Save to: data/log/incubator_history.json"
echo "  - Keep last $MAX_HOURS hours of data"
if [[ -z "$NO_PUSH" ]]; then
    echo "  - Automatically push to GitHub"
else
    echo "  - NOT push to GitHub (disabled)"
fi
echo ""
echo "Monitor the logger:"
echo "  tail -f logs/logger.log"
echo ""
echo "View the data:"
echo "  python view_history.py"
echo ""
echo "Check cron jobs:"
echo "  crontab -l"
echo ""
echo "Remove cron job:"
echo "  crontab -e"
echo "  (then delete the line with memmert_logger.py)"
echo ""
