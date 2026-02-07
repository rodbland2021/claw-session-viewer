#!/usr/bin/env python3
"""
Real-time Session Viewer for OpenClaw
Shows active sessions, token usage, and live transcript tails
"""

from flask import Flask, render_template_string, jsonify, request
import json
import os
import glob
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

AGENTS_DIR = os.path.expanduser("~/.openclaw/agents")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Session Viewer</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, monospace;
            background: #0d1117;
            color: #c9d1d9;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #58a6ff; margin-bottom: 20px; }
        
        .sessions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .session-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 15px;
            cursor: pointer;
            transition: border-color 0.2s;
        }
        .session-card:hover { border-color: #58a6ff; }
        .session-card.selected { border-color: #58a6ff; background: #1c2128; }
        
        .session-name {
            font-weight: bold;
            color: #58a6ff;
            margin-bottom: 8px;
            font-size: 14px;
            word-break: break-all;
        }
        
        .session-stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 10px;
            font-size: 12px;
        }
        
        .stat {
            background: #21262d;
            padding: 8px;
            border-radius: 4px;
            text-align: center;
        }
        .stat-label { color: #8b949e; font-size: 10px; }
        .stat-value { color: #f0f6fc; font-weight: bold; margin-top: 2px; }
        .stat-value.warning { color: #d29922; }
        .stat-value.danger { color: #f85149; }
        
        .usage-bar {
            height: 4px;
            background: #21262d;
            border-radius: 2px;
            margin-top: 10px;
            overflow: hidden;
        }
        .usage-fill {
            height: 100%;
            background: #238636;
            transition: width 0.3s;
        }
        .usage-fill.warning { background: #d29922; }
        .usage-fill.danger { background: #f85149; }
        
        .transcript-viewer {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
        }
        
        .transcript-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 1px solid #30363d;
        }
        
        .transcript-title { color: #58a6ff; font-size: 16px; }
        
        .controls {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            background: #21262d;
            border: 1px solid #30363d;
            color: #c9d1d9;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
        }
        .btn:hover { background: #30363d; }
        .btn.active { background: #238636; border-color: #238636; }
        
        .transcript-content {
            max-height: 600px;
            overflow-y: auto;
            font-size: 13px;
            line-height: 1.5;
        }
        
        .entry {
            padding: 12px;
            margin-bottom: 8px;
            border-radius: 6px;
            border-left: 3px solid #30363d;
        }
        .entry.user { background: #1c3a5f; border-left-color: #58a6ff; }
        .entry.assistant { background: #1c2d1c; border-left-color: #238636; }
        .entry.tool_use { background: #2d2a1c; border-left-color: #d29922; }
        .entry.tool_result { background: #2d1c2a; border-left-color: #a371f7; }
        .entry.system { background: #21262d; border-left-color: #8b949e; }
        
        .entry-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 6px;
            font-size: 11px;
            color: #8b949e;
            gap: 8px;
        }

        .entry-meta {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .entry-timestamp {
            color: #6e7681;
            font-family: monospace;
            font-size: 10px;
            white-space: nowrap;
        }
        
        .entry-role {
            font-weight: bold;
            text-transform: uppercase;
        }
        .entry-role.user { color: #58a6ff; }
        .entry-role.assistant { color: #238636; }
        .entry-role.tool_use { color: #d29922; }
        .entry-role.tool_result { color: #a371f7; }
        
        .entry-size {
            background: #21262d;
            padding: 2px 6px;
            border-radius: 3px;
        }
        .entry-size.large { background: #d29922; color: #000; }
        .entry-size.huge { background: #f85149; color: #fff; }
        
        .entry-content {
            white-space: pre-wrap;
            word-break: break-word;
            max-height: 300px;
            overflow-y: auto;
        }
        
        .entry-content.truncated::after {
            content: "... [truncated]";
            color: #8b949e;
            font-style: italic;
        }
        
        .refresh-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #238636;
            color: #fff;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            opacity: 0;
            transition: opacity 0.3s;
        }
        .refresh-indicator.visible { opacity: 1; }
        
        .no-session {
            text-align: center;
            color: #8b949e;
            padding: 40px;
        }
        
        .image-placeholder {
            background: #30363d;
            padding: 10px;
            border-radius: 4px;
            color: #8b949e;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Session Viewer</h1>
        
        <div class="sessions-grid" id="sessions"></div>
        
        <div class="transcript-viewer" id="transcript-viewer" style="display: none;">
            <div class="transcript-header">
                <div class="transcript-title" id="transcript-title">Select a session</div>
                <div class="controls">
                    <button class="btn" id="btn-tail" onclick="toggleTail()">📡 Live Tail</button>
                    <button class="btn" onclick="refreshTranscript()">🔄 Refresh</button>
                    <label style="display: flex; align-items: center; gap: 5px; font-size: 12px;">
                        <input type="checkbox" id="show-tools" checked onchange="refreshTranscript()"> Show Tools
                    </label>
                </div>
            </div>
            <div class="transcript-content" id="transcript"></div>
        </div>
    </div>
    
    <div class="refresh-indicator" id="refresh-indicator">Refreshed</div>
    
    <script>
        let selectedSession = null;
        let tailInterval = null;
        let lastEntryCount = 0;
        
        function formatBytes(bytes) {
            if (bytes < 1024) return bytes + ' B';
            if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
            return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
        
        function formatTokens(tokens) {
            if (tokens < 1000) return tokens;
            return (tokens / 1000).toFixed(1) + 'K';
        }
        
        function getUsageClass(pct) {
            if (pct >= 85) return 'danger';
            if (pct >= 70) return 'warning';
            return '';
        }
        
        function getSizeClass(chars) {
            if (chars > 50000) return 'huge';
            if (chars > 10000) return 'large';
            return '';
        }

        function formatTimestamp(ts) {
            if (!ts) return '';
            try {
                const d = new Date(ts);
                const pad = n => String(n).padStart(2, '0');
                return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
            } catch(e) {
                return ts;
            }
        }
        
        async function loadSessions() {
            const res = await fetch('/api/sessions');
            const sessions = await res.json();
            
            const container = document.getElementById('sessions');
            container.innerHTML = sessions.map(s => {
                const pct = s.contextTokens > 0 ? Math.round(s.totalTokens / s.contextTokens * 100) : 0;
                const usageClass = getUsageClass(pct);
                return `
                    <div class="session-card ${selectedSession === s.key ? 'selected' : ''}" 
                         onclick="selectSession('${s.key}')">
                        <div class="session-name">${s.displayName || s.key}</div>
                        <div style="font-size: 11px; color: #8b949e; margin-bottom: 8px;">${s.model || 'unknown'} &middot; ${formatTokens(s.contextTokens)} ctx</div>
                        <div class="session-stats">
                            <div class="stat">
                                <div class="stat-label">Tokens</div>
                                <div class="stat-value ${usageClass}">${formatTokens(s.totalTokens)}</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Context</div>
                                <div class="stat-value">${pct}%</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">File</div>
                                <div class="stat-value">${formatBytes(s.fileSize)}</div>
                            </div>
                        </div>
                        <div class="usage-bar">
                            <div class="usage-fill ${usageClass}" style="width: ${pct}%"></div>
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        async function selectSession(key) {
            selectedSession = key;
            document.getElementById('transcript-viewer').style.display = 'block';
            loadSessions();
            refreshTranscript();
        }
        
        async function refreshTranscript() {
            if (!selectedSession) return;
            
            const showTools = document.getElementById('show-tools').checked;
            const res = await fetch(`/api/transcript?key=${encodeURIComponent(selectedSession)}&tools=${showTools}`);
            const data = await res.json();
            
            document.getElementById('transcript-title').textContent = 
                `${data.displayName || selectedSession} — ${data.entries.length} entries`;
            
            const container = document.getElementById('transcript');
            container.innerHTML = data.entries.map((e, i) => {
                const sizeClass = getSizeClass(e.chars);
                let content = e.content;
                
                // Truncate very long content
                if (content.length > 2000) {
                    content = content.substring(0, 2000);
                }
                
                // Handle images
                content = content.replace(/\[Image: [^\]]+\]/g, 
                    '<div class="image-placeholder">📷 [Image data]</div>');
                
                return `
                    <div class="entry ${e.role}">
                        <div class="entry-header">
                            <div class="entry-meta">
                                <span class="entry-role ${e.role}">${e.role}${e.toolName ? ': ' + e.toolName : ''}</span>
                                <span class="entry-timestamp">${formatTimestamp(e.timestamp)}</span>
                            </div>
                            <span class="entry-size ${sizeClass}">${formatBytes(e.chars)} / ~${formatTokens(e.estimatedTokens)} tokens</span>
                        </div>
                        <div class="entry-content ${content.length >= 2000 ? 'truncated' : ''}">${escapeHtml(content)}</div>
                    </div>
                `;
            }).join('');
            
            // Auto-scroll to top if tail is on and new entries (newest first)
            if (tailInterval && data.entries.length > lastEntryCount) {
                container.scrollTop = 0;
                showRefreshIndicator();
            }
            lastEntryCount = data.entries.length;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function toggleTail() {
            const btn = document.getElementById('btn-tail');
            if (tailInterval) {
                clearInterval(tailInterval);
                tailInterval = null;
                btn.classList.remove('active');
            } else {
                tailInterval = setInterval(refreshTranscript, 2000);
                btn.classList.add('active');
                refreshTranscript();
            }
        }
        
        function showRefreshIndicator() {
            const indicator = document.getElementById('refresh-indicator');
            indicator.classList.add('visible');
            setTimeout(() => indicator.classList.remove('visible'), 1000);
        }
        
        // Initial load
        loadSessions();
        setInterval(loadSessions, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/sessions')
def api_sessions():
    sessions = []
    
    for agent_dir in glob.glob(f"{AGENTS_DIR}/*/sessions"):
        sessions_json = os.path.join(agent_dir, "sessions.json")
        if not os.path.exists(sessions_json):
            continue
            
        try:
            with open(sessions_json) as f:
                data = json.load(f)
            
            for key, entry in data.items():
                session_id = entry.get('sessionId', '')
                session_file = os.path.join(agent_dir, f"{session_id}.jsonl")
                file_size = os.path.getsize(session_file) if os.path.exists(session_file) else 0
                
                sessions.append({
                    'key': key,
                    'displayName': entry.get('displayName', key),
                    'totalTokens': entry.get('totalTokens', 0) or 0,
                    'contextTokens': entry.get('contextTokens', 200000) or 200000,
                    'inputTokens': entry.get('inputTokens', 0) or 0,
                    'outputTokens': entry.get('outputTokens', 0) or 0,
                    'model': entry.get('model', 'unknown'),
                    'updatedAt': entry.get('updatedAt', 0),
                    'fileSize': file_size,
                    'sessionFile': session_file
                })
        except Exception as e:
            continue
    
    # Sort by most recently updated
    sessions.sort(key=lambda x: x.get('updatedAt', 0), reverse=True)
    return jsonify(sessions)

@app.route('/api/transcript')
def api_transcript():
    key = request.args.get('key', '')
    show_tools = request.args.get('tools', 'true') == 'true'
    
    # Find the session
    session_file = None
    display_name = key
    
    for agent_dir in glob.glob(f"{AGENTS_DIR}/*/sessions"):
        sessions_json = os.path.join(agent_dir, "sessions.json")
        if not os.path.exists(sessions_json):
            continue
        try:
            with open(sessions_json) as f:
                data = json.load(f)
            if key in data:
                entry = data[key]
                session_id = entry.get('sessionId', '')
                session_file = os.path.join(agent_dir, f"{session_id}.jsonl")
                display_name = entry.get('displayName', key)
                break
        except:
            continue
    
    if not session_file or not os.path.exists(session_file):
        return jsonify({'entries': [], 'displayName': display_name})
    
    entries = []
    try:
        with open(session_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    entry_type = obj.get('type', '')
                    
                    timestamp = obj.get('timestamp', '')

                    # Handle compaction entries
                    if entry_type == 'compaction':
                        summary = obj.get('summary', '')
                        tokens_before = obj.get('tokensBefore', 0)
                        entries.append({
                            'role': 'system',
                            'toolName': 'compaction',
                            'content': f"[COMPACTION - {tokens_before} tokens before]\n{summary[:1000]}...",
                            'chars': len(summary),
                            'estimatedTokens': len(summary) // 4,
                            'timestamp': timestamp
                        })
                        continue

                    # Only process message entries
                    if entry_type != 'message':
                        continue

                    # Extract message object
                    msg = obj.get('message', {})
                    role = msg.get('role', 'unknown')
                    content_parts = msg.get('content', [])

                    # Process content
                    for part in content_parts if isinstance(content_parts, list) else [content_parts]:
                        if isinstance(part, str):
                            text = part
                            entry_role = role
                            tool_name = None
                        elif isinstance(part, dict):
                            part_type = part.get('type', '')

                            if part_type == 'text':
                                text = part.get('text', '')
                                entry_role = role
                                tool_name = None
                            elif part_type == 'tool_use':
                                if not show_tools:
                                    continue
                                tool_name = part.get('name', 'unknown')
                                tool_input = part.get('input', {})
                                text = json.dumps(tool_input, indent=2)[:5000]
                                entry_role = 'tool_use'
                            elif part_type == 'tool_result':
                                if not show_tools:
                                    continue
                                tool_name = part.get('tool_use_id', '')[:8]
                                result = part.get('content', '')
                                if isinstance(result, list):
                                    result = ' '.join(str(r.get('text', r)) for r in result if isinstance(r, dict))
                                text = str(result)[:5000]
                                entry_role = 'tool_result'
                            elif part_type == 'image':
                                text = '[Image: base64 data]'
                                entry_role = role
                                tool_name = None
                            else:
                                continue
                        else:
                            continue

                        char_count = len(text)
                        entries.append({
                            'role': entry_role,
                            'toolName': tool_name,
                            'content': text,
                            'chars': char_count,
                            'estimatedTokens': char_count // 4,
                            'timestamp': timestamp
                        })
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        pass
    
    # Reverse so latest entries appear first
    entries.reverse()

    return jsonify({
        'entries': entries,
        'displayName': display_name
    })

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8766)
    args = parser.parse_args()
    
    print(f"📊 Session Viewer running at http://localhost:{args.port}")
    app.run(host=args.host, port=args.port, threaded=True)
