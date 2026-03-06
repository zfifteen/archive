#!/bin/bash

# === CONFIGURATION ===
INTERVAL_MINUTES=30
# =====================

export PATH="/usr/local/bin:/opt/homebrew/bin:$PATH"
# Set PATH so launchd can find gemini (adjust if installed elsewhere)

LOG_DIR="$HOME/logs"
mkdir -p "$LOG_DIR"

while true; do
    LOGFILE="$LOG_DIR/gemini-daily-$(date +%Y-%m-%d).log"

    echo "=== Run started: $(date) ===" | tee -a "$LOGFILE"
    gemini -y -p /Users/velocityworks/IdeaProjects/tasks/prompts/money-updated.md 2>&1 | tee -a "$LOGFILE"
    echo "=== Run finished: $(date) ===" | tee -a "$LOGFILE"

    # Calculate seconds until the next aligned interval boundary
    CURRENT_MIN=$(date +%M | sed 's/^0//')
    CURRENT_SEC=$(date +%S | sed 's/^0//')

    MINS_INTO_INTERVAL=$(( CURRENT_MIN % INTERVAL_MINUTES ))
    MINS_LEFT=$(( INTERVAL_MINUTES - MINS_INTO_INTERVAL ))

    SECS_LEFT=$(( (MINS_LEFT * 60) - CURRENT_SEC ))

    # Guard against negative or zero sleep
    if [ "$SECS_LEFT" -le 0 ]; then
        SECS_LEFT=$(( INTERVAL_MINUTES * 60 ))
    fi

    echo "Sleeping ${SECS_LEFT}s until next ${INTERVAL_MINUTES}-minute mark..." | tee -a "$LOGFILE"
    sleep "$SECS_LEFT"
done
