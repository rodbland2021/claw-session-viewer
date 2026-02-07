# Changelog

All notable changes to Claw Session Viewer will be documented in this file.

## [1.0.0] - 2026-02-07

### Added
- Initial release
- Session grid view with token usage visualization
- Live transcript viewer with role-based color coding
- Timestamp display for all entries
- Auto-refresh and live tail mode
- Tool use/result filtering
- Context usage percentage bars with color coding
- Support for all OpenClaw agents
- REST API endpoints for session data and transcripts
- Automatic session discovery from `~/.openclaw/agents/`

### Features
- **Multi-agent support** - View sessions across all configured agents
- **Real-time monitoring** - Auto-refresh every 5 seconds, live tail every 2 seconds
- **Token tracking** - Monitor context window usage with visual indicators
- **Entry filtering** - Toggle tool use/result visibility
- **Responsive design** - Works on desktop and mobile browsers
- **Lightweight** - Single Python file, minimal dependencies
