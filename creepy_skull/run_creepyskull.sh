#!/bin/bash

# --- Configuration ---
SCRIPT="creepy_skull_triggered.py"
LOGFILE="creepy_skull_triggered.log"
PYTHON=$(which python3)

echo "🔧 Launching Floating Skull..."
echo "📜 Logging to $LOGFILE"
echo "🐍 Using Python interpreter: $PYTHON"
echo "-----------------------------"

# --- Run the script ---
$PYTHON $SCRIPT >> $LOGFILE 2>&1
