# shell-capture

⚠️ **WARNING: This is a Proof-of-Concept (PoC) tool. DO NOT use in production!**

An experimental terminal wrapper attempting to provide tmux-capture-like functionality. **This tool is NOT recommended for actual use** and serves only as a feasibility validation. Use `tmux-capture` instead for real-world needs.

## Why You Shouldn't Use This

1. **Performance Overhead**: Adds ~10-15% performance penalty compared to native execution
2. **Untested**: No comprehensive test suite - expect unknown behaviors and edge cases  
3. **Incomplete Implementation**: Missing many features and proper error handling
4. **Better Alternative Exists**: `tmux-capture` is mature, tested, and production-ready
5. **Experimental Status**: This is a PoC with no maintenance or support

## Performance Analysis

Based on `render-test.sh` benchmark results:

| Environment | Execution Time | Performance Impact |
|-------------|----------------|-------------------|
| Direct tmux shell | 17.916s | Baseline |
| shell-capture in tmux | 19.822s | **+10.6% slower** |
| Direct terminal | 17.154s | Baseline |

**Key Findings:**
- shell-capture adds approximately 1.9 seconds overhead (~10.6% performance penalty)
- Increased system CPU usage due to additional I/O processing
- Memory overhead from buffer management and terminal emulation

## Experimental Features (Untested)

- **Transparent Shell Proxy**: Attempts to wrap shell commands with terminal emulation
- **Global Hotkey**: Press `Ctrl+E` to enter capture mode (may not work reliably)
- **Pattern Matching**: Tries to find URLs, git commits, emails, file paths
- **Interactive Selection**: Vim-style hints for text selection (experimental)
- **Terminal Emulation**: Uses `pyte` library for VT100+ compatibility (incomplete)

## Recommended Alternative

**Use tmux-capture instead:**

```bash
# Install tmux-capture (mature, tested solution)
pip install tmux-capture

# Use tmux-capture for reliable terminal capture
tmux-capture [options]
```

## Usage (At Your Own Risk)

⚠️ **Disclaimer**: This tool may crash, produce unexpected results, or behave unpredictably.

```bash
# Basic usage (experimental)
./shell-capture <command>

# Examples (use with caution)
./shell-capture bash
./shell-capture "ls -la"
```

## What This PoC Demonstrates

1. **Feasibility**: Terminal capture without tmux dependency is technically possible
2. **Performance Cost**: Significant overhead (~10.6%) makes it impractical  
3. **Complexity**: Terminal emulation is complex and error-prone
4. **Value of tmux-capture**: Existing solution is superior in every way

## Requirements

- Python 3.10+
- `uv` package manager (for automatic dependency installation)
- Dependencies (automatically installed):
  - `blessed >= 1.21.0` - Terminal control and rendering
  - `ptyprocess >= 0.7.0` - PTY process management
  - `pyte >= 0.8.1` - Terminal emulation engine
- Clipboard utilities:
  - macOS: `pbcopy` (built-in)
  - Linux: `xclip` or `xsel`

## Architecture

Shell-capture creates a comprehensive terminal emulation wrapper around your shell command using modern Python libraries:

1. **PTY Management**: Uses `ptyprocess` to spawn and control shell processes
2. **Terminal Emulation**: Employs `pyte` library for complete VT100+ terminal emulation
3. **Real-time Rendering**: Uses `blessed` for cross-platform terminal control and true color support
4. **I/O Multiplexing**: Select-based non-blocking I/O for transparent forwarding
5. **Screen Buffer**: Maintains complete 2D screen state with history scrollback
6. **Pattern Recognition**: Integrates tmux-capture's mature pattern matching engine
7. **Alternative Screen Support**: Full vim/tmux compatibility with screen buffer switching

## Comparison: shell-capture vs tmux-capture

| Feature | shell-capture (PoC) | tmux-capture (Recommended) |
|---------|-------------------|---------------------------|
| **Stability** | ❌ Experimental, untested | ✅ Mature, well-tested |
| **Performance** | ❌ 10.6% overhead | ✅ Minimal overhead |
| **Maintenance** | ❌ No support/updates | ✅ Actively maintained |
| **Features** | ❌ Incomplete, buggy | ✅ Full feature set |
| **Dependencies** | ❌ Complex Python deps | ✅ Simple tmux dependency |
| **Error Handling** | ❌ Minimal, crashes | ✅ Robust error handling |
| **Documentation** | ❌ Experimental only | ✅ Comprehensive docs |
| **Community** | ❌ None | ✅ Active community |

## Development Status

**Status**: ⚠️ Experimental / Abandoned

This PoC was created to explore whether terminal capture could work without tmux. While technically feasible, the experiment conclusively shows that:

1. **Performance penalty is too high** (~10.6% overhead)
2. **Complexity is overwhelming** (terminal emulation is hard)
3. **tmux-capture is simply better** in every meaningful way

## Conclusion

**Recommendation**: Use `tmux-capture` for any real-world terminal capture needs. This PoC demonstrates why reinventing the wheel is unnecessary when excellent solutions already exist.

---

*This project serves as a testament to the quality and value of the existing tmux-capture ecosystem.*
