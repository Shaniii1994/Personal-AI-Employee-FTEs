# Personal AI Employee FTEs

## Project Overview

This project implements a **Digital FTE (Full-Time Equivalent)** — an autonomous AI employee built using **Claude Code** as the reasoning engine and **Obsidian** as the knowledge dashboard. The system runs 24/7, managing personal and business affairs through a local-first, agent-driven architecture.

**Core Concept:** Instead of waiting for user input, the AI Employee uses "Watcher" scripts to monitor inputs (Gmail, WhatsApp, filesystems) and proactively takes action via MCP (Model Context Protocol) servers, with human-in-the-loop approval for sensitive operations.

**Key Innovation:** The "Ralph Wiggum" persistence pattern keeps Claude working autonomously until tasks are complete, transforming it from a chatbot into a proactive employee.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    PERCEPTION LAYER                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │Gmail Watcher│  │WhatsApp     │  │FileSystem Watcher   │  │
│  │             │  │Watcher      │  │(Drop folders)       │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    REASONING LAYER                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Claude Code + Ralph Wiggum Loop                    │    │
│  │  - Reads /Needs_Action folder                       │    │
│  │  - Creates Plan.md for complex tasks                │    │
│  │  - Writes approval requests to /Pending_Approval    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                     ACTION LAYER                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │Email MCP    │  │Browser MCP  │  │Human-in-the-Loop    │  │
│  │(Send/Draft) │  │(Playwright) │  │(/Approved folder)   │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY LAYER (Obsidian)                  │
│  Dashboard.md | Company_Handbook.md | Business_Goals.md    │
│  /Inbox | /Needs_Action | /Done | /Pending_Approval        │
└─────────────────────────────────────────────────────────────┘
```

## Directory Structure

```
Personal-AI-Employee-FTEs/
├── .qwen/
│   ├── plugins/
│   │   └── ralph_wiggum.py       # Persistence loop plugin
│   └── skills/
│       └── browsing-with-playwright/
│           ├── SKILL.md           # Playwright MCP documentation
│           ├── references/
│           │   └── playwright-tools.md
│           └── scripts/
│               ├── mcp-client.py  # MCP client utility
│               ├── start-server.sh
│               ├── stop-server.sh
│               └── verify.py
├── QWEN.md                        # This file
└── Personal AI Employee Hackathon 0_...md  # Full hackathon guide
```

## Key Components

### 1. Ralph Wiggum Plugin (`.qwen/plugins/ralph_wiggum.py`)

A stop-hook plugin that intercepts Claude's exit attempts and checks if the task is complete:
- **Completion Detection:** Looks for `TASK_COMPLETE` patterns or file movement to `/Done`
- **Continuation:** Re-injects prompts to keep Claude working until done
- **Max Iterations:** Prevents infinite loops (default: 10)

### 2. Browsing with Playwright Skill

Browser automation via Playwright MCP server for web-based actions:
- **Server Management:** Start/stop scripts with `--shared-browser-context` flag
- **Tools:** Navigate, click, type, fill forms, screenshots, JavaScript evaluation
- **Verification:** `python scripts/verify.py` to check server status

### 3. Watcher Scripts (To Be Implemented)

Lightweight Python scripts that monitor external systems:
- **Gmail Watcher:** Polls Gmail API for unread/important messages
- **WhatsApp Watcher:** Uses Playwright to monitor WhatsApp Web
- **FileSystem Watcher:** Watches drop folders using `watchdog` library

## Building and Running

### Prerequisites

| Component | Version | Purpose |
|-----------|---------|---------|
| Claude Code | Active subscription | Reasoning engine |
| Obsidian | v1.10.6+ | Knowledge base/GUI |
| Python | 3.13+ | Watcher scripts |
| Node.js | v24+ LTS | MCP servers |

### Setup Steps

1. **Create Obsidian Vault:**
   ```bash
   mkdir AI_Employee_Vault
   cd AI_Employee_Vault
   mkdir Inbox Needs_Action Done Pending_Approval Plans Updates
   ```

2. **Install Playwright MCP:**
   ```bash
   npx @playwright/mcp@latest --port 8808 --shared-browser-context &
   ```

3. **Verify Setup:**
   ```bash
   python scripts/verify.py
   ```

4. **Install Ralph Wiggum Plugin:**
   ```bash
   # Copy to global Claude plugins folder
   cp .qwen/plugins/ralph_wiggum.py ~/.claude/plugins/
   ```

### Running the AI Employee

**Basic Mode (Interactive):**
```bash
claude "Check /Needs_Action folder and process any pending items"
```

**Ralph Loop Mode (Autonomous):**
```bash
claude --plugin ralph_wiggum "Process all emails in /Needs_Action, draft replies, and move to /Done when complete"
```

**Scheduled Mode (via cron/Task Scheduler):**
```bash
# Linux/Mac cron example (daily 8 AM briefing)
0 8 * * * claude "Generate Monday Morning CEO Briefing from Business_Goals.md and this week's transactions"
```

### Watcher Scripts (Background Processes)

```bash
# Gmail Watcher
python watchers/gmail_watcher.py &

# WhatsApp Watcher
python watchers/whatsapp_watcher.py &

# FileSystem Watcher
python watchers/filesystem_watcher.py &
```

## Development Conventions

### File Naming Patterns

| Pattern | Purpose |
|---------|---------|
| `EMAIL_{id}.md` | Processed emails |
| `WHATSAPP_{chat}_{timestamp}.md` | WhatsApp messages |
| `FILE_{original_name}.md` | Dropped files |
| `PLAN_{task}_{date}.md` | Task plans |
| `APPROVAL_{action}_{recipient}.md` | Approval requests |

### Markdown Schema

All action files use YAML frontmatter:

```yaml
---
type: email
from: sender@example.com
subject: Invoice Request
received: 2026-01-07T10:30:00Z
priority: high
status: pending
---
```

### Human-in-the-Loop Pattern

For sensitive actions (payments, sending messages):

1. Claude writes to `/Pending_Approval/{action}.md`
2. User reviews and moves file to `/Approved` or `/Rejected`
3. Orchestrator detects approval and executes via MCP

### Error Handling

- **Watcher Scripts:** Log errors, continue running (graceful degradation)
- **MCP Failures:** Retry 3 times, then write error file to `/Needs_Action`
- **Ralph Loop:** Max iterations prevent infinite loops

## Testing Practices

### Unit Testing Watchers

```python
# Test watcher creates correct file format
def test_gmail_watcher_creates_valid_md():
    watcher = GmailWatcher(vault_path, credentials_path)
    filepath = watcher.create_action_file(test_message)
    assert filepath.exists()
    assert '---' in filepath.read_text()  # Has frontmatter
    assert 'type: email' in filepath.read_text()
```

### Integration Testing

1. Drop test file in `/Needs_Action`
2. Run Claude with Ralph plugin
3. Verify file moved to `/Done`
4. Check expected actions were taken

## MCP Server Configuration

Configure in `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["/path/to/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json"
      }
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@playwright/mcp"],
      "env": {
        "HEADLESS": "true"
      }
    }
  ]
}
```

## Security Considerations

- **Secrets Management:** Never commit `.env` files, tokens, or credentials
- **Vault Sync:** Only sync markdown/state files, never secrets
- **Approval Workflow:** All payments/messages require human approval before sending
- **Audit Logging:** All actions logged with timestamps

## Common Commands

```bash
# Start Playwright MCP server
bash .qwen/skills/browsing-with-playwright/scripts/start-server.sh

# Stop Playwright MCP server
bash .qwen/skills/browsing-with-playwright/scripts/stop-server.sh

# Verify server is running
python .qwen/skills/browsing-with-playwright/scripts/verify.py

# Run Claude with Ralph plugin
claude --plugin ralph_wiggum "Your task here"

# Check server process
pgrep -f "@playwright/mcp"
```

## Resources

- **Full Hackathon Guide:** `Personal AI Employee Hackathon 0_ Building Autonomous FTEs in 2026.md`
- **Ralph Wiggum Reference:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum
- **Playwright MCP:** https://github.com/microsoft/playwright-mcp
- **MCP Overview:** https://modelcontextprotocol.io/
