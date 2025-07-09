#!/usr/bin/env zsh

# tmux-capture.plugin.zsh
# Zsh plugin for tmux-capture with command-line hotkey support

# Default hotkey configuration
(( ! ${+TMUX_CAPTURE_HOTKEY} )) && typeset -g TMUX_CAPTURE_HOTKEY='^E'

# Get the directory where this script is located
TMUX_CAPTURE_DIR="${0:A:h}"
TMUX_CAPTURE_SCRIPT="$TMUX_CAPTURE_DIR/tmux-capture"

# Function to launch tmux-capture
tmux-capture-widget() {
    # Check if we're in a tmux session
    if [[ -n "$TMUX" ]]; then
        # Inside tmux - use the window script for better integration
        local window_script="$TMUX_CAPTURE_DIR/tmux-capture-window.sh"
        if [[ -f "$window_script" ]]; then
            "$window_script"
        else
            # Fallback to direct execution
            "$TMUX_CAPTURE_SCRIPT"
        fi
    else
        # Outside tmux - show error message
        echo "Error: tmux-capture requires a tmux session"
        echo "Start tmux first: tmux new-session"
        return 1
    fi
}

# Create zsh widget
zle -N tmux-capture-widget

# Bind to configured hotkey
bindkey "$TMUX_CAPTURE_HOTKEY" tmux-capture-widget

# Function to show help
tmux-capture-help() {
    echo "tmux-capture zsh plugin"
    echo ""
    echo "Usage:"
    echo "  $TMUX_CAPTURE_HOTKEY           - Launch tmux-capture (inside tmux)"
    echo "  tmux-capture     - Launch tmux-capture directly"
    echo ""
    echo "Configuration:"
    echo "  TMUX_CAPTURE_HOTKEY - Set hotkey (default: ^E)"
    echo "  Example: export TMUX_CAPTURE_HOTKEY='^O'"
    echo ""
    echo "Note: All commands require an active tmux session"
}