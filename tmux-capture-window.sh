#!/bin/bash

# tmux-capture-window.sh
# Script to launch tmux-capture in a new tmux window

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAPTURE_SCRIPT="$SCRIPT_DIR/tmux-capture"

# Check if we're running inside tmux
if [ -z "$TMUX" ]; then
    echo "Error: This script must be run inside a tmux session"
    exit 1
fi

# Check if tmux-capture exists
if [ ! -f "$CAPTURE_SCRIPT" ]; then
    tmux display-message "Error: tmux-capture not found at $CAPTURE_SCRIPT"
    exit 1
fi

# Get the current pane ID that we want to capture
CURRENT_PANE=$(tmux display-message -p "#{pane_id}")

# Create a new window with a descriptive name
NEW_WINDOW_NAME="capture-$(date +%s)"

# Create new window and run the capture script using uv
# The script will run in interactive mode and wait for user input before closing
tmux new-window -n "$NEW_WINDOW_NAME" -c "$SCRIPT_DIR" \
    "uv run --script '$CAPTURE_SCRIPT' '$CURRENT_PANE' && exit 0"

# The window will automatically close after the script finishes
# Thanks to the "tmux kill-window" command appended to the python command
