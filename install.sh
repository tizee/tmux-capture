#!/bin/bash

# install.sh
# Installation script for tmux-capture

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMUX_CONF=${TMUX_CONF:-"$HOME/.config/tmux/tmux.conf"}

echo "Installing tmux-capture..."

# Make scripts executable
chmod +x "$SCRIPT_DIR/tmux-capture-window.sh"
chmod +x "$SCRIPT_DIR/tmux-capture"
echo "✓ Made scripts executable"

# Check if tmux.conf exists
if [ ! -f "$TMUX_CONF" ]; then
    echo "Creating new tmux.conf..."
    touch "$TMUX_CONF"
fi

# Create the configuration line
CONFIG_LINE="bind-key y run-shell '$SCRIPT_DIR/tmux-capture-window.sh'"

# Check if the binding already exists
if grep -q "bind-key y run-shell.*tmux-capture" "$TMUX_CONF"; then
    echo "⚠ tmux-capture binding already exists in $TMUX_CONF"
    echo "You may need to manually update the path"
else
    echo "" >> "$TMUX_CONF"
    echo "# tmux-capture binding" >> "$TMUX_CONF"
    echo "$CONFIG_LINE" >> "$TMUX_CONF"
    echo "✓ Added tmux-capture binding to $TMUX_CONF"
fi

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

echo ""
echo -e "${GREEN}✓ Installation complete!${NC}"
echo ""
echo -e "${WHITE}Usage:${NC}"
echo -e "${CYAN}1.${NC} Reload tmux config: ${YELLOW}tmux source-file ~/.tmux.conf${NC}"
echo -e "${CYAN}2.${NC} In tmux, press ${YELLOW}Prefix + y${NC} to launch capture tool"
echo -e "${CYAN}3.${NC} The capture tool will open in a new window showing the original pane content"
echo -e "${CYAN}4.${NC} Select text using keyboard hints and it will be copied to clipboard"
echo -e "${CYAN}5.${NC} After selection or cancellation, press any key to close the window"
echo ""
echo -e "${WHITE}Optional: Add to PATH for CLI usage${NC}"
echo -e "Add this to your ${MAGENTA}~/.zshrc${NC} or ${MAGENTA}~/.bashrc${NC}:"
echo -e "${YELLOW}export PATH=\"$SCRIPT_DIR:\$PATH\"${NC}"
echo -e "${YELLOW}alias tc='tmux-capture'${NC}"
echo ""
echo -e "${WHITE}For zsh users: Enable command-line hotkey (${YELLOW}Ctrl+E${WHITE} by default)${NC}"
echo -e "Add this to your ${MAGENTA}~/.zshrc${NC}:"
echo -e "${YELLOW}source \"$SCRIPT_DIR/tmux-capture.plugin.zsh\"${NC}"
echo ""
echo -e "${WHITE}To customize hotkey, set ${CYAN}TMUX_CAPTURE_HOTKEY${WHITE} before sourcing:${NC}"
echo -e "${YELLOW}export TMUX_CAPTURE_HOTKEY='^O'${NC}  ${BLUE}# Use Ctrl+O instead${NC}"
echo ""
echo -e "${RED}Note:${NC} Make sure you have ${YELLOW}'uv'${NC} installed"
echo -e "Install uv with: ${YELLOW}curl -LsSf https://astral.sh/uv/install.sh | sh${NC}"
echo ""
echo -e "${BLUE}The tool will capture content from the pane where you pressed the key combination,${NC}"
echo -e "${BLUE}not from the new window where the tool runs.${NC}"
