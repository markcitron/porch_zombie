#!/bin/bash

# --- Configuration ---
SCRIPT="mqtt_skull_motion.py"
LOGFILE="mqtt_skull_motion.log"
PYTHON=$(which python3)

echo "🔧 Launching Floating Skull..."
echo "📜 Logging to $LOGFILE"
echo "🐍 Using Python interpreter: $PYTHON"
echo "-----------------------------"

# --- Run the script ---
$PYTHON $SCRIPT >> $LOGFILE 2>&1
