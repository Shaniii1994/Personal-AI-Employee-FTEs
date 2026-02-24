---
name: filesystem-watcher
description: |
  Monitor a drop folder for new files and create action items in the AI Employee vault.
  Use when you need to process files dropped into a folder, automate file intake,
  or create a hands-off file submission workflow.
---

# FileSystem Watcher Skill

Monitor a folder for new files and automatically create actionable items for Qwen to process.

## Overview

The FileSystem Watcher is a **Bronze Tier** AI Employee skill that:
- Watches a designated "drop folder" for new files
- Creates markdown action files with metadata
- Copies files to the Needs_Action folder
- Logs all activity for audit purposes
- Supports both event-driven (real-time) and polling modes

## Installation

### Step 1: Install Dependencies

```bash
cd AI_Employee_Vault/watchers
pip install -r requirements.txt
```

### Step 2: Verify Installation

```bash
python filesystem_watcher.py --help
```

Expected output shows vault path and drop folder configuration.

## Usage

### Basic Usage

```bash
# Start the watcher (event-driven mode)
python watchers/filesystem_watcher.py

# Start with custom vault path
python watchers/filesystem_watcher.py /path/to/vault

# Start in polling mode (fallback)
python watchers/filesystem_watcher.py --polling
```

### Processing Dropped Files with Qwen

Once the watcher is running:

```bash
# Process all pending file drops
qwen "Check /Needs_Action folder and process all file drops"

# Process with Ralph Wiggum for autonomy
qwen --plugin ralph_wiggum "Process all files in /Needs_Action, analyze content, and move to /Done when complete"
```

## How It Works

### Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   User drops    │────▶│  FileSystem      │────▶│  Action file    │
│   file in Inbox │     │  Watcher         │     │  in Needs_Action│
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Move to Done   │◀────│  Qwen processes  │◀────│  Human reviews  │
│  when complete  │     │  and takes action│     │  if needed      │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### File Flow

1. **Drop:** User (or another system) drops a file into `Inbox/`
2. **Detect:** Watcher detects the new file (within 5 seconds)
3. **Hash:** File is hashed for deduplication
4. **Copy:** File is copied to `Needs_Action/` with timestamp
5. **Metadata:** Action file (.md) created with:
   - YAML frontmatter (type, size, hash, timestamp)
   - File information section
   - Suggested actions checklist
6. **Process:** Qwen reads and processes the action file
7. **Complete:** Items moved to `Done/` when finished

## Action File Format

When a file is dropped, the watcher creates:

### Original File Copy
```
Needs_Action/FILEDROP_invoice.pdf_20260225_103045.pdf
```

### Action File (.md)
```markdown
---
type: file_drop
original_name: invoice.pdf
dropped_name: FILEDROP_invoice.pdf_20260225_103045.pdf
size: 245678
size_human: 239.92 KB
received: 2026-02-25T10:30:45.123456
modified: 2026-02-25T09:15:30
hash: a1b2c3d4e5f6...
status: pending
priority: normal
---

# File Drop for Processing

## File Information

- **Original Name:** invoice.pdf
- **Stored As:** FILEDROP_invoice.pdf_20260225_103045.pdf
- **Size:** 239.92 KB
- **Received:** 2026-02-25T10:30:45

## Content Preview

<!-- AI Employee: Analyze this file and suggest actions -->

## Suggested Actions

- [ ] Review file content
- [ ] Categorize file type
- [ ] Take appropriate action
- [ ] Move to /Done when complete

## Notes

<!-- Add any additional context or instructions here -->

---
*Created by FileSystemWatcher v0.1.0*
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VAULT_PATH` | Current dir | Path to Obsidian vault |
| `DROP_FOLDER` | `Inbox/` | Folder to monitor |
| `CHECK_INTERVAL` | `5` | Seconds between checks (polling mode) |
| `USE_POLLING` | `false` | Force polling mode |

### Code Configuration

Edit `filesystem_watcher.py`:

```python
# Custom check interval
watcher = FileSystemWatcher(vault_path, check_interval=10)

# Custom drop folder
watcher = FileSystemWatcher(vault_path, drop_folder="/path/to/drops")

# Force polling mode
watcher = FileSystemWatcher(vault_path, use_polling=True)
```

## Examples

### Example 1: Process Invoice PDF

**User Action:**
Drop `invoice_jan2026.pdf` into `Inbox/`

**Watcher Creates:**
- `FILEDROP_invoice_jan2026.pdf_20260225_103045.pdf`
- `FILEDROP_invoice_jan2026.pdf_20260225_103045.md`

**Qwen Processes:**
```bash
qwen "Process the invoice file drop in Needs_Action"
```

**Qwen Output:**
- Reads the PDF content
- Extracts amount, vendor, date
- Creates entry in `Accounting/Current_Month.md`
- Moves files to `Done/`

### Example 2: Batch File Processing

**User Action:**
Drop multiple files into `Inbox/`

**Watcher Creates:**
- Action file for each dropped file

**Qwen Processes:**
```bash
qwen "Process all file drops in Needs_Action, categorize each file"
```

### Example 3: Automated Document Intake

**Setup:**
Configure email-to-file-drop automation (e.g., IFTTT or Zapier saves attachments to `Inbox/`)

**Watcher:**
Automatically creates action files for each attachment

**Qwen:**
Processes and categorizes documents daily

## Integration Patterns

### Pattern 1: Email Attachments

```
Email → Save Attachment → Inbox/ → Watcher → Qwen → Done
```

### Pattern 2: Screenshot Processing

```
Screenshot tool → Save to Inbox/ → Watcher → Qwen (OCR) → Notes
```

### Pattern 3: Receipt Capture

```
Mobile app → Upload to cloud folder → Sync to Inbox/ → Watcher → Qwen → Accounting
```

## Troubleshooting

### Issue: Watcher Not Detecting Files

**Solutions:**
1. Check logs: `Logs/watcher_YYYY-MM-DD.log`
2. Verify folder permissions
3. Ensure file is not a `.md` file (skipped by design)
4. Try polling mode: `python filesystem_watcher.py --polling`

### Issue: Duplicate Processing

**Solutions:**
1. Check `processed_state.json` in vault root
2. Verify file hash is being calculated
3. Delete state file to reset: `rm processed_state.json`

### Issue: Large Files Slow

**Solutions:**
1. Increase check interval for large files
2. Consider file size limits in watcher
3. Use polling mode for better control

## Best Practices

### File Naming
- Use descriptive names: `invoice_acme_jan2026.pdf` not `doc1.pdf`
- Include dates when relevant
- Avoid special characters

### Folder Organization
- Keep `Inbox/` for raw incoming files only
- Review `Needs_Action/` daily
- Archive `Done/` monthly

### Qwen Prompts
- Be specific: "Process invoice files and log to Accounting"
- Set expectations: "Move to Done when complete"
- Request summaries: "Summarize what you processed"

## Security Considerations

- ✅ Files stay local in vault
- ✅ All actions logged
- ✅ File hashing prevents duplicates
- ⚠️ Sensitive files should be encrypted before dropping
- ⚠️ Review logs regularly for anomalies

## Performance

| Metric | Value |
|--------|-------|
| Detection latency | < 5 seconds (event-driven) |
| File copy speed | ~100 MB/s |
| Max file size | Limited by disk space |
| Memory usage | ~50 MB |

## Future Enhancements (Silver/Gold Tier)

- [ ] File type detection (auto-categorize)
- [ ] OCR integration for images
- [ ] Cloud folder sync (Dropbox, Google Drive)
- [ ] Multi-folder monitoring
- [ ] Priority-based processing
- [ ] File quarantine for suspicious files

## Related Skills

- **Gmail Watcher** - Monitor Gmail for important emails
- **WhatsApp Watcher** - Monitor WhatsApp for urgent messages
- **Ralph Wiggum Plugin** - Keep Qwen working autonomously

## Reference

- [Base Watcher Class](watchers/base_watcher.py)
- [FileSystem Watcher](watchers/filesystem_watcher.py)
- [Company Handbook](Company_Handbook.md)
- [Dashboard](Dashboard.md)

---

*FileSystem Watcher Skill v0.1.0*
*Bronze Tier - AI Employee Hackathon 0*
