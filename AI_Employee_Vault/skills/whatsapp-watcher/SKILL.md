---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for urgent messages and create action items in the AI Employee vault.
  Uses Playwright for browser automation. Use when you need to track WhatsApp messages,
  auto-process urgent communications, or create WhatsApp-based workflows.
---

# WhatsApp Watcher Skill

Monitor WhatsApp Web for urgent messages and automatically create actionable items for Qwen to process.

## Overview

The WhatsApp Watcher is a **Silver Tier** AI Employee skill that:
- Monitors WhatsApp Web using Playwright browser automation
- Detects unread messages with urgent keywords
- Creates markdown action files with message metadata
- Maintains persistent browser session
- Logs all activity for audit purposes

## Prerequisites

### 1. Install Dependencies

```bash
cd AI_Employee_Vault/watchers
pip install playwright
playwright install chromium
```

### 2. WhatsApp Web Access

- Ensure you have a WhatsApp account
- Be aware of WhatsApp's Terms of Service
- Use at your own risk (automation may violate ToS)

## Usage

### Basic Usage

```bash
# Start the watcher (interactive - shows browser)
python watchers/whatsapp_watcher.py

# Start in headless mode (no browser window)
python watchers/whatsapp_watcher.py --headless

# Start with custom keywords
python watchers/whatsapp_watcher.py --keywords "urgent,asap,invoice,payment,help"
```

### First Run - QR Code Scan

1. Run the watcher
2. Browser opens to WhatsApp Web
3. Scan QR code with your phone
4. Session is saved for future runs

### Processing Messages with Qwen

```bash
# Process all pending messages
qwen "Check /Needs_Action and process all WhatsApp messages"

# Process urgent messages first
qwen "Process WhatsApp messages in Needs_Action, prioritize urgent ones, draft responses"
```

## Action File Format

When a WhatsApp message is detected, the watcher creates:

```markdown
---
type: whatsapp
from: +1234567890
chat_name: John Doe
received: 2026-02-25T10:30:00Z
priority: high
status: pending
keywords_matched: urgent, invoice
session_hash: a1b2c3d4e5f6
---

# WhatsApp Message for Processing

## Sender Information
- **From:** +1234567890
- **Chat:** John Doe
- **Received:** 2026-02-25T10:30:00Z

## Message Content

{message_text}

## Urgency Indicators
- Keywords matched: urgent, invoice
- Priority: HIGH

## Suggested Actions

- [ ] Reply to sender
- [ ] Take immediate action
- [ ] Forward to relevant party
- [ ] Mark as read in WhatsApp

## Notes

<!-- Add any additional context or instructions here -->

---
*Created by WhatsAppWatcher v0.1.0*
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `VAULT_PATH` | No | Path to Obsidian vault |
| `SESSION_PATH` | No | Path to store browser session |
| `CHECK_INTERVAL` | No | Seconds between checks (default: 30) |
| `KEYWORDS` | No | Comma-separated urgent keywords |
| `HEADLESS` | No | Run browser in background (default: false) |

### Code Configuration

```python
# Custom keywords
watcher = WhatsAppWatcher(
    vault_path='/path/to/vault',
    keywords=['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency']
)

# Custom check interval
watcher = WhatsAppWatcher(vault_path, check_interval=60)

# Headless mode
watcher = WhatsAppWatcher(vault_path, headless=True)
```

## Examples

### Example 1: Invoice Requests

**Setup:** Monitor for invoice-related keywords

```python
watcher = WhatsAppWatcher(
    vault_path,
    keywords=['invoice', 'payment', 'bill', 'money']
)
```

**Qwen Processes:**
```bash
qwen "Process WhatsApp invoice requests, create invoices, send payment details"
```

### Example 2: Emergency Contacts

**Setup:** Monitor for emergency keywords from specific contacts

```python
watcher = WhatsAppWatcher(
    vault_path,
    keywords=['emergency', 'urgent', 'asap', 'help']
)
```

**Qwen Processes:**
```bash
qwen "Process emergency WhatsApp messages, prioritize and alert immediately"
```

### Example 3: Customer Support

**Setup:** Monitor business WhatsApp for customer inquiries

```python
watcher = WhatsAppWatcher(
    vault_path,
    keywords=['question', 'help', 'support', 'issue', 'problem']
)
```

**Qwen Processes:**
```bash
qwen "Process customer support messages, categorize issues, draft responses"
```

## Integration Patterns

### Pattern 1: Message → Response Draft
```
WhatsApp → Watcher → Needs_Action → Qwen → Draft reply
                                        → Mark as read
```

### Pattern 2: Message → Task Creation
```
WhatsApp → Watcher → Needs_Action → Qwen → Create task
                                            → Assign priority
```

### Pattern 3: Message → Alert
```
Urgent WhatsApp → Watcher → Needs_Action → Qwen → Send alert
                                                    → Notify human
```

## Troubleshooting

### Issue: QR Code Expired

**Solutions:**
1. Delete session folder: `rm -rf ~/.whatsapp_session`
2. Restart watcher
3. Scan QR code promptly (30 second timeout)

### Issue: Browser Won't Start

**Solutions:**
1. Verify Playwright installed: `playwright install chromium`
2. Check for browser conflicts
3. Try headless mode: `python whatsapp_watcher.py --headless`

### Issue: Messages Not Detected

**Solutions:**
1. Verify WhatsApp Web is loaded
2. Check keywords match message content
3. Review logs: `Logs/watcher_YYYY-MM-DD.log`
4. Ensure session is authenticated

### Issue: Session Lost

**Solutions:**
1. Session file may be corrupted
2. Delete session and re-authenticate
3. Check disk space for session storage

## Security Considerations

- ✅ Session stored locally (not synced)
- ✅ No message content stored permanently
- ✅ All processing logged
- ⚠️ WhatsApp ToS may prohibit automation
- ⚠️ Use personal account at own risk
- ⚠️ Consider using WhatsApp Business API for production

## Performance

| Metric | Value |
|--------|-------|
| Check interval | 30 seconds (configurable) |
| Browser memory | ~200 MB |
| Processing time per message | < 2 seconds |
| Session persistence | Until logout/clear |

## Best Practices

1. **Run in background:** Use headless mode for production
2. **Monitor keywords:** Adjust based on your needs
3. **Review regularly:** Check processed messages daily
4. **Backup session:** Copy session folder for recovery
5. **Rate limiting:** Don't check too frequently (WhatsApp may block)

## Related Skills

- **Gmail Watcher** - Monitor Gmail for important emails
- **FileSystem Watcher** - Monitor local file drops
- **Approval Workflow** - Human-in-the-loop for sensitive actions
- **LinkedIn Poster** - Post to social media

## Reference

- [Playwright Documentation](https://playwright.dev/python/)
- [WhatsApp Web](https://web.whatsapp.com/)
- [Base Watcher Class](watchers/base_watcher.py)
- [Company Handbook](Company_Handbook.md)

---

*WhatsApp Watcher Skill v0.1.0*
*Silver Tier - AI Employee Hackathon 0*
