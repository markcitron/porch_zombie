#!/bin/bash

# --- Configuration ---
SCRIPT="scarecrow_main.py"
LOGFILE="scarecrow.log"
PYTHON=$(which python3)

echo "🔧 Launching Scarecrow..."
echo "📜 Logging to $LOGFILE"
echo "🐍 Using Python interpreter: $PYTHON"
echo "-----------------------------"

# --- Run the script ---
$PYTHON $SCRIPT >> $LOGFILE 2>&1
