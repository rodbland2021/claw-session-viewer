# Quick Start Guide

Get up and running with Claw Session Viewer in under 2 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/claw-session-viewer.git
cd claw-session-viewer

# Install dependencies
pip install -r requirements.txt

# Run the viewer
python session-viewer.py
```

## First Use

1. **Open your browser** to http://localhost:8766

2. **View sessions** - All active OpenClaw sessions appear as cards showing:
   - Session name/ID
   - Model name (e.g., claude-sonnet-4-5, gpt-4o)
   - Token usage
   - Context percentage
   - File size

3. **Click a session** to view its full transcript

4. **Use the controls**:
   - **📡 Live Tail** - Auto-refresh every 2 seconds
   - **🔄 Refresh** - Manual refresh
   - **Show Tools** - Toggle tool use/result visibility

## Understanding the Display

### Session Cards

Each session shows three metrics:

- **Tokens**: Current token count (green = normal, amber = high, red = critical)
- **Context**: Percentage of context window used
- **File**: Size of the session file on disk

### Usage Bar Colors

- **Green**: 0-69% (healthy)
- **Amber**: 70-84% (getting full)
- **Red**: 85%+ (nearing limit)

### Transcript Entry Colors

- **Blue** - User messages
- **Green** - Assistant responses
- **Amber** - Tool calls
- **Purple** - Tool results
- **Gray** - System messages

## Tips

1. **Live monitoring**: Enable "Live Tail" to watch conversations in real-time
2. **Hide tools**: Uncheck "Show Tools" for a cleaner view of user/assistant messages
3. **Scroll**: Newest messages appear at the top - scroll down for history
4. **Multiple sessions**: Open multiple tabs to monitor different sessions simultaneously

## Next Steps

- Read the [full README](README.md) for advanced usage
- Check the [API documentation](#api-endpoints) for integrations
- See [CHANGELOG](CHANGELOG.md) for version history

## Troubleshooting

**No sessions showing?**
- Make sure OpenClaw is running
- Check that `~/.openclaw/agents/*/sessions/` exists
- Verify you have permission to read the session files

**Port already in use?**
```bash
python session-viewer.py --port 9000
```

**Need help?**
- Open an issue on GitHub
- Join the OpenClaw community discussions
