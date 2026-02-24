# AI Employee Vault - Setup & Usage Guide

## Quick Start

### Prerequisites

1. **Python 3.13+** - Download from [python.org](https://www.python.org/downloads/)
2. **Qwen Code** - Active subscription
3. **Obsidian** - v1.10.6+ (free)

### Installation

#### Step 1: Install Python Dependencies

```bash
cd watchers
pip install -r requirements.txt
```

#### Step 2: Start the FileSystem Watcher

**Event-driven mode (recommended, requires watchdog):**
```bash
python watchers/filesystem_watcher.py
```

**Polling mode (fallback):**
```bash
python watchers/filesystem_watcher.py --polling
```

#### Step 3: Drop a File to Test

1. Drop any file (PDF, image, document, etc.) into the `Inbox/` folder
2. Watch the watcher create an action file in `Needs_Action/`
3. Check the logs in `Logs/` folder

#### Step 4: Process with Qwen Code

```bash
cd AI_Employee_Vault
qwen "Check /Needs_Action folder and process all pending file drops"
```

## Folder Structure

```
AI_Employee_Vault/
├── Dashboard.md           # Main dashboard
├── Company_Handbook.md    # Rules and guidelines
├── Inbox/                 # Drop files here for processing
├── Needs_Action/          # Action files created by watchers
├── Pending_Approval/      # Awaiting human approval
├── Approved/              # Ready for action
├── Done/                  # Completed items
├── Plans/                 # Task plans
├── Logs/                  # Watcher and action logs
├── Briefings/             # CEO briefings
├── Accounting/            # Financial records
└── watchers/              # Watcher scripts
    ├── base_watcher.py
    ├── filesystem_watcher.py
    └── requirements.txt
```

## How It Works

### FileSystem Watcher (Bronze Tier)

1. **You drop a file** into `Inbox/` folder
2. **Watcher detects** the new file (real-time via watchdog)
3. **Action file created** in `Needs_Action/` with:
   - YAML frontmatter (metadata)
   - File information
   - Suggested actions checklist
4. **Qwen processes** the action file when prompted
5. **Task completed** - files moved to `Done/`

### Example Flow

```
1. Drop: invoice.pdf → Inbox/
2. Watcher creates:
   - FILEDROP_invoice.pdf_20260225_103045.md → Needs_Action/
   - FILEDROP_invoice.pdf_20260225_103045.pdf → Needs_Action/ (copy)
3. Run Qwen:
   qwen "Process file drops in Needs_Action"
4. Qwen:
   - Reads the action file
   - Analyzes the PDF
   - Creates plan if needed
   - Takes action or requests approval
5. Move completed items to Done/
```

## Commands Reference

### Watcher Commands

```bash
# Start watcher (event-driven)
python watchers/filesystem_watcher.py

# Start watcher (polling mode)
python watchers/filesystem_watcher.py --polling

# Start with custom vault path
python watchers/filesystem_watcher.py /path/to/vault

# Stop watcher
# Press Ctrl+C
```

### Qwen Code Commands

```bash
# Process pending items
qwen "Check /Needs_Action and process all pending items"

# Generate daily briefing
qwen "Generate daily briefing from Dashboard and recent activity"

# With Ralph Wiggum plugin (autonomous mode)
qwen --plugin ralph_wiggum "Process all files in /Needs_Action, move to /Done when complete"
```

## Configuration

### Watcher Settings

Edit `filesystem_watcher.py` to customize:

```python
# Check interval (seconds)
check_interval = 5  # Default: 5 seconds

# Drop folder location
drop_folder = vault_path / 'Inbox'  # Default: Inbox folder

# Use polling instead of event-driven
use_polling = False  # Default: False (event-driven)
```

### Company Handbook Rules

Edit `Company_Handbook.md` to customize:
- Payment thresholds
- Approval requirements
- Communication tone
- File retention policies

## Troubleshooting

### Watcher Not Detecting Files

1. **Check logs:** `Logs/watcher_YYYY-MM-DD.log`
2. **Verify drop folder:** Ensure files go to `Inbox/`
3. **Restart watcher:** Stop (Ctrl+C) and restart
4. **Check permissions:** Ensure read/write access

### Qwen Not Processing Correctly

1. **Review Company Handbook:** Ensure rules are clear
2. **Check action file format:** Verify YAML frontmatter
3. **Provide more context:** Add notes to action file
4. **Use Ralph Wiggum:** For complex multi-step tasks

### Python Not Found

**Windows:**
```bash
# Install Python from Microsoft Store or python.org
# Then use:
py -m pip install -r requirements.txt
py watchers/filesystem_watcher.py
```

**Mac/Linux:**
```bash
# Install Python 3.13+
brew install python@3.13  # Mac
sudo apt install python3.13 python3-pip  # Linux

python3 -m pip install -r requirements.txt
python3 watchers/filesystem_watcher.py
```

## Next Steps (Silver Tier)

After mastering the Bronze Tier:

1. **Gmail Watcher** - Monitor Gmail for important emails
2. **WhatsApp Watcher** - Monitor WhatsApp for urgent messages
3. **MCP Servers** - Enable external actions (send email, etc.)
4. **Approval Workflow** - Human-in-the-loop for sensitive actions
5. **Scheduled Briefings** - Daily/weekly CEO briefings

## Security Notes

- ✅ Credentials never stored in vault
- ✅ All actions logged to `Logs/` folder
- ✅ Human approval required for sensitive actions
- ✅ Local-first architecture (privacy-focused)

## Support

For issues or questions:
1. Check logs in `Logs/` folder
2. Review `Company_Handbook.md` rules
3. Consult the main hackathon document

---

*AI Employee v0.1.0 (Bronze Tier)*
*Built with Qwen Code + Obsidian*
