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
        # Show output and wait for user confirmation in tmux environment
        local window_script="$TMUX_CAPTURE_DIR/tmux-capture-window.sh"
        if [[ -f "$window_script" ]]; then
            "$window_script"
        else
            # Fallback to direct execution
            "$TMUX_CAPTURE_SCRIPT"
        fi
    else
        # Outside tmux - check if tmux is running and has sessions
        if ! command -v tmux >/dev/null 2>&1; then
            echo "Error: tmux command not found"
            return 1
        fi

        # Check if any tmux sessions exist
        if ! tmux list-sessions >/dev/null 2>&1; then
            echo "Error: No tmux sessions found"
            echo "Start tmux first: tmux new-session"
            return 1
        fi

        # Get current tmux session's default pane
        local current_session=$(tmux display-message -p '#S' 2>/dev/null)
        if [[ -z "$current_session" ]]; then
            # No current session, get the first available session
            current_session=$(tmux list-sessions -F '#S' | head -1)
        fi

        if [[ -n "$current_session" ]]; then
            # Get the current window and pane of the session
            local current_pane=$(tmux list-panes -t "$current_session" -F '#{pane_id}' | head -1)
            if [[ -n "$current_pane" ]]; then
                # tmux-capture now has native terminal control - no redirection needed
                "$TMUX_CAPTURE_SCRIPT" "$current_pane"
            else
                echo "Error: No panes found in tmux session '$current_session'"
                return 1
            fi
        else
            echo "Error: Unable to determine tmux session"
            return 1
        fi
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
    echo "  $TMUX_CAPTURE_HOTKEY           - Launch tmux-capture (works inside/outside tmux)"
    echo "  tmux-capture     - Launch tmux-capture directly"
    echo ""
    echo "Configuration:"
    echo "  TMUX_CAPTURE_HOTKEY - Set hotkey (default: ^E)"
    echo "  Example: export TMUX_CAPTURE_HOTKEY='^O'"
    echo ""
    echo "Note: Requires tmux to be running with at least one session"
}
