#!/bin/bash

# tmux-capture launcher script for TPM
# This script runs tmux-capture in a popup overlay

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CAPTURE_SCRIPT="$CURRENT_DIR/tmux-capture"

# Check if tmux-capture exists
if [ ! -f "$CAPTURE_SCRIPT" ]; then
    tmux display-message "Error: tmux-capture not found at $CAPTURE_SCRIPT"
    exit 1
fi

# Get the current pane ID that we want to capture
CURRENT_PANE=$(tmux display-message -p "#{pane_id}")

# Use display-popup to overlay the capture interface
# -E: execute the command
# -w/h: size (90% of viewport)
# -b "heavy": border style
tmux display-popup -E -w 90% -h 90% -b "heavy" \
    "cd '$CURRENT_DIR' && uv run --script '$CAPTURE_SCRIPT' '$CURRENT_PANE'"
