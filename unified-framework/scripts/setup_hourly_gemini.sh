#!/bin/bash
set -e

OLD_LABEL="com.bigD.gemini-daily"
NEW_LABEL="com.bigD.gemini-hourly"
OLD_PLIST="$HOME/Library/LaunchAgents/${OLD_LABEL}.plist"
NEW_PLIST="$HOME/Library/LaunchAgents/${NEW_LABEL}.plist"
LOG_DIR="$HOME/logs"

echo "=== Gemini LaunchAgent: Daily → Hourly ==="

# --- Step 1: Remove the old daily task ---
echo "[1/4] Unloading old task: ${OLD_LABEL}"
if launchctl list | grep -q "${OLD_LABEL}"; then
    launchctl unload "${OLD_PLIST}" 2>/dev/null && echo "  ✓ Unloaded" || echo "  ⚠ Already unloaded"
else
    echo "  ⚠ Not currently loaded, skipping unload"
fi

if [ -f "${OLD_PLIST}" ]; then
    rm "${OLD_PLIST}"
    echo "  ✓ Deleted ${OLD_PLIST}"
else
    echo "  ⚠ Plist file not found at ${OLD_PLIST}"
fi

# --- Step 2: Ensure log directory exists ---
echo "[2/4] Ensuring log directory exists"
mkdir -p "${LOG_DIR}"
echo "  ✓ ${LOG_DIR}"

# --- Step 3: Create the new hourly plist ---
echo "[3/4] Creating new hourly task: ${NEW_LABEL}"
cat > "${NEW_PLIST}" << 'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.bigD.gemini-hourly</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/Users/velocityworks/IdeaProjects/tasks/scripts/daily_gemini.sh</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/velocityworks/logs/gemini_hourly.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/velocityworks/logs/gemini_hourly_error.log</string>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
PLIST
echo "  ✓ Written to ${NEW_PLIST}"

# --- Step 4: Load the new task ---
echo "[4/4] Loading new task"
launchctl load "${NEW_PLIST}"
echo "  ✓ Loaded"

# --- Verify ---
echo ""
echo "=== Verification ==="
echo "Old task gone:"
launchctl list | grep "${OLD_LABEL}" && echo "  ✗ STILL LOADED" || echo "  ✓ Removed"
echo "New task active:"
launchctl list | grep "${NEW_LABEL}" && echo "  ✓ Running" || echo "  ✗ NOT FOUND"

echo ""
echo "Done. Gemini will now run at the top of every hour, 24/7."
echo "To test immediately: launchctl start ${NEW_LABEL}"
