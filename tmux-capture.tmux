#!/usr/bin/env bash

CURRENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set the script path as a tmux option so other scripts can reference it
tmux set-option -gq "@tmux-capture-path" "$CURRENT_DIR"

# Set default keybinding if not already set
if [ -z "$(tmux show-option -gv "@tmux-capture-key")" ]; then
    tmux set-option -g "@tmux-capture-key" "y"
fi

# Bind the key based on @tmux-capture-key option
capture_key="$(tmux show-option -gv "@tmux-capture-key")"
tmux bind-key "$capture_key" run-shell "$CURRENT_DIR/scripts/capture.sh"
