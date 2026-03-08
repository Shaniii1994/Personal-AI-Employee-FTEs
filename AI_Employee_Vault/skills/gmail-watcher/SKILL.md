---
name: gmail-watcher
description: |
  Monitor Gmail for important/unread emails and create action items in the AI Employee vault.
  Use when you need to track important emails, auto-process inbox, or create email-based workflows.
  Requires Gmail API credentials setup.
---

# Gmail Watcher Skill

Monitor Gmail for important emails and automatically create actionable items for Qwen to process.

## Overview

The Gmail Watcher is a **Silver Tier** AI Employee skill that:
- Polls Gmail API for unread/important emails
- Creates markdown action files with email metadata
- Tracks processed emails to avoid duplicates
- Logs all activity for audit purposes
- Supports customizable check intervals

## Prerequisites

### 1. Google Cloud Project Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`

### 2. Install Dependencies

```bash
cd AI_Employee_Vault/watchers
pip install -r requirements.txt
```

### 3. Authenticate

```bash
python -m gmail_watcher --authenticate
```

This opens a browser window for OAuth authentication.

## Usage

### Basic Usage

```bash
# Start the watcher
python watchers/gmail_watcher.py

# Start with custom check interval (seconds)
python watchers/gmail_watcher.py --interval 60

# Start in dry-run mode (no action files created)
python watchers/gmail_watcher.py --dry-run
```

### Processing Emails with Qwen

```bash
# Process all pending emails
qwen "Check /Needs_Action and process all email items"

# Process with specific instructions
qwen "Process emails in Needs_Action, draft replies for urgent ones, move to Done when complete"
```

## Action File Format

When an email is detected, the watcher creates:

```markdown
---
type: email
from: sender@example.com
to: me@myemail.com
subject: Invoice Request
received: 2026-02-25T10:30:00Z
priority: high
status: pending
gmail_id: 18d4f2a3b5c6e7f8
labels: IMPORTANT,UNREAD
---

# Email for Processing

## Sender Information
- **From:** sender@example.com
- **Subject:** Invoice Request
- **Received:** 2026-02-25T10:30:00Z

## Email Content

{email_snippet_or_body}

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Mark as read in Gmail

## Notes

<!-- Add any additional context or instructions here -->

---
*Created by GmailWatcher v0.1.0*
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GMAIL_CREDENTIALS` | Yes | Path to `credentials.json` |
| `GMAIL_TOKEN` | Yes | Path to stored OAuth token |
| `VAULT_PATH` | No | Path to Obsidian vault |
| `CHECK_INTERVAL` | No | Seconds between checks (default: 120) |
| `GMAIL_QUERY` | No | Gmail search query (default: `is:unread is:important`) |

### Code Configuration

```python
# Custom query for specific emails
watcher = GmailWatcher(
    vault_path='/path/to/vault',
    credentials_path='/path/to/credentials.json',
    gmail_query='from:client@example.com is:unread'
)

# Custom check interval
watcher = GmailWatcher(vault_path, credentials_path, check_interval=300)
```

## Examples

### Example 1: Process Client Emails

**Setup:** Configure watcher to monitor emails from specific client

```python
watcher = GmailWatcher(
    vault_path,
    credentials_path,
    gmail_query='from:client@company.com is:unread'
)
```

**Qwen Processes:**
```bash
qwen "Process client emails, extract action items, draft responses"
```

### Example 2: Invoice Requests

**Setup:** Monitor for invoice-related emails

```python
watcher = GmailWatcher(
    vault_path,
    credentials_path,
    gmail_query='subject:invoice OR subject:payment is:unread'
)
```

**Qwen Processes:**
```bash
qwen "Process invoice emails, create accounting entries, send invoices"
```

### Example 3: Support Tickets

**Setup:** Monitor support email address

```python
watcher = GmailWatcher(
    vault_path,
    credentials_path,
    gmail_query='to:support@mycompany.com is:unread'
)
```

**Qwen Processes:**
```bash
qwen "Process support emails, categorize by urgency, draft responses"
```

## Integration Patterns

### Pattern 1: Email → Task
```
Gmail → Watcher → Needs_Action → Qwen → Done
                              → Task created
```

### Pattern 2: Email → Reply Draft
```
Gmail → Watcher → Needs_Action → Qwen → Draft reply
                                      → Mark as read
```

### Pattern 3: Email → Accounting
```
Invoice Email → Watcher → Needs_Action → Qwen → Accounting log
                                              → Send invoice
```

## Troubleshooting

### Issue: Authentication Failed

**Solutions:**
1. Verify `credentials.json` is valid
2. Re-run authentication: `python -m gmail_watcher --authenticate`
3. Check Gmail API is enabled in Google Cloud Console
4. Verify OAuth consent screen is configured

### Issue: No Emails Detected

**Solutions:**
1. Check Gmail query is correct
2. Verify emails are marked as unread/important
3. Check `processed_state.json` for already-processed IDs
4. Review logs: `Logs/watcher_YYYY-MM-DD.log`

### Issue: API Rate Limit

**Solutions:**
1. Increase check interval (default: 120s)
2. Implement exponential backoff
3. Use Gmail push notifications instead of polling

## Security Considerations

- ✅ OAuth 2.0 authentication (no passwords stored)
- ✅ Token stored securely
- ✅ All email processing logged
- ⚠️ Never commit `token.json` to version control
- ⚠️ Review Gmail API permissions regularly

## Performance

| Metric | Value |
|--------|-------|
| Check interval | 120 seconds (configurable) |
| API calls per check | 1-2 |
| Memory usage | ~30 MB |
| Processing time per email | < 1 second |

## Related Skills

- **FileSystem Watcher** - Monitor local file drops
- **WhatsApp Watcher** - Monitor WhatsApp messages
- **Email MCP** - Send emails via Gmail API
- **Approval Workflow** - Human-in-the-loop for sensitive actions

## Reference

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [Google OAuth 2.0 Guide](https://developers.google.com/identity/protocols/oauth2)
- [Base Watcher Class](watchers/base_watcher.py)
- [Company Handbook](Company_Handbook.md)

---

*Gmail Watcher Skill v0.1.0*
*Silver Tier - AI Employee Hackathon 0*
