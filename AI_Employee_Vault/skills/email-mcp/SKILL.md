---
name: email-mcp
description: |
  Send, draft, and manage emails via Gmail API.
  Use when the AI Employee needs to send emails, create drafts,
  or manage Gmail communications. Requires Gmail API credentials.
---

# Email MCP Skill

Send and manage emails via Gmail API as an MCP (Model Context Protocol) server.

## Overview

The Email MCP is a **Silver Tier** AI Employee skill that:
- Sends emails via Gmail API
- Creates draft emails for review
- Searches and reads emails
- Manages labels and folders
- Supports attachments

## Prerequisites

### 1. Gmail API Setup

Same as Gmail Watcher:
1. Google Cloud Project
2. Gmail API enabled
3. OAuth 2.0 credentials
4. `credentials.json` downloaded

### 2. Install Dependencies

```bash
cd AI_Employee_Vault/watchers
pip install -r requirements.txt
```

## Usage

### Start Email MCP Server

```bash
# Start the MCP server
python watchers/email_mcp_server.py

# Server runs on localhost:8809 by default
```

### Send Email via Qwen

```bash
# Send email directly (for non-sensitive)
qwen "Send email to client@example.com with subject 'Invoice Attached' and body 'Please find attached your invoice.'"

# Create draft for review (recommended)
qwen "Draft an email to client@example.com requesting payment for invoice #123"
```

## Email Actions

### Send Email

```python
# MCP Tool: email_send
{
    "to": "recipient@example.com",
    "subject": "Invoice #123",
    "body": "Please find attached your invoice.",
    "attachments": ["/path/to/invoice.pdf"]
}
```

### Create Draft

```python
# MCP Tool: email_draft
{
    "to": "recipient@example.com",
    "subject": "Invoice #123",
    "body": "Please find attached your invoice.",
    "cc": ["accounting@example.com"]
}
```

### Search Emails

```python
# MCP Tool: email_search
{
    "query": "from:client@example.com is:unread",
    "max_results": 10
}
```

### Read Email

```python
# MCP Tool: email_read
{
    "email_id": "18d4f2a3b5c6e7f8"
}
```

### Mark as Read

```python
# MCP Tool: email_mark_read
{
    "email_ids": ["18d4f2a3b5c6e7f8"]
}
```

## Human-in-the-Loop Pattern

For sensitive emails, always create approval request first:

```markdown
# /Pending_Approval/EMAIL_send_invoice_123.md

---
type: approval_request
action: email_send
to: client@example.com
subject: Invoice #123
created: 2026-02-25T10:30:00Z
---

## Email to Send

**To:** client@example.com
**Subject:** Invoice #123
**Body:** Please find attached your invoice for January services.

**Attachment:** invoice_123.pdf

---
Move to /Approved to send, or /Rejected to discard.
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GMAIL_CREDENTIALS` | Yes | Path to `credentials.json` |
| `GMAIL_TOKEN` | Yes | Path to stored OAuth token |
| `MCP_PORT` | No | Server port (default: 8809) |
| `DRY_RUN` | No | Log but don't send (default: true) |

### MCP Configuration

Add to `~/.config/claude-code/mcp.json`:

```json
{
  "servers": [
    {
      "name": "email",
      "command": "python",
      "args": ["/path/to/email_mcp_server.py"],
      "env": {
        "GMAIL_CREDENTIALS": "/path/to/credentials.json",
        "DRY_RUN": "false"
      }
    }
  ]
}
```

## Examples

### Example 1: Send Invoice

**Qwen Command:**
```bash
qwen "Send invoice #123 to client@example.com with PDF attachment"
```

**MCP Call:**
```python
email_send(
    to="client@example.com",
    subject="Invoice #123 - January 2026",
    body="Dear Client, Please find attached your invoice for January 2026 services. Payment is due within 30 days.",
    attachments=["/Vault/Invoices/invoice_123.pdf"]
)
```

### Example 2: Draft Response

**Qwen Command:**
```bash
qwen "Draft a response to the inquiry email"
```

**MCP Call:**
```python
email_draft(
    to="inquiry@example.com",
    subject="Re: Service Inquiry",
    body="Thank you for your interest. We would be happy to discuss...",
    cc=["sales@mycompany.com"]
)
```

### Example 3: Search and Process

**Qwen Command:**
```bash
qwen "Find all unread emails from VIP clients and create action items"
```

**MCP Call:**
```python
results = email_search(query="from:vip@company.com is:unread")
for email in results:
    create_action_file(email)
```

## Security Considerations

- ✅ OAuth 2.0 authentication
- ✅ No passwords stored
- ✅ All sent emails logged
- ✅ DRY_RUN mode for testing
- ⚠️ Always require approval for new recipients
- ⚠️ Never auto-send to more than 5 recipients
- ⚠️ Review sent items daily

## Error Handling

| Error | Recovery |
|-------|----------|
| Authentication failed | Re-authenticate, check credentials |
| Rate limit | Wait 60 seconds, retry |
| Invalid recipient | Flag for human review |
| Attachment not found | Log error, continue |

## Best Practices

1. **Always draft first:** Create draft for human review
2. **Approval for new contacts:** Never auto-email new recipients
3. **Log everything:** All sends logged to audit file
4. **Rate limiting:** Max 10 emails per minute
5. **Test mode:** Use DRY_RUN=true during development

## Related Skills

- **Gmail Watcher** - Monitor incoming emails
- **Approval Workflow** - Human-in-the-loop for sending
- **Plan Creator** - Plan email campaigns

## Reference

- [Gmail API Documentation](https://developers.google.com/gmail/api)
- [MCP Specification](https://modelcontextprotocol.io/)
- [Company Handbook](Company_Handbook.md)

---

*Email MCP Skill v0.1.0*
*Silver Tier - AI Employee Hackathon 0*
