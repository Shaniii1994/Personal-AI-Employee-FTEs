# 📧 Gmail Watcher - Setup Guide

Complete setup guide for Gmail Watcher with OAuth 2.0 authentication.

---

## Prerequisites

- ✅ Python 3.13+ installed
- ✅ Gmail API dependencies installed
- ✅ `credentials.json` in project root

---

## Step 1: Verify credentials.json

Your `credentials.json` should be at:
```
C:\Users\shani\Documents\Personal-AI-Employee-FTEs\credentials.json
```

**Expected content:**
```json
{
  "installed": {
    "client_id": "...",
    "project_id": "...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "client_secret": "...",
    "redirect_uris": ["http://localhost"]
  }
}
```

---

## Step 2: Run Authentication

Open terminal and run:

```bash
cd C:\Users\shani\Documents\Personal-AI-Employee-FTEs\AI_Employee_Vault\watchers
python3 gmail_watcher.py --authenticate
```

**What happens:**
1. Browser opens automatically
2. Google login page appears
3. Sign in with your Gmail account
4. Grant permissions to the app
5. Browser shows "Authentication successful"
6. `token.json` is created

---

## Step 3: Verify Token Created

After authentication, check:
```
C:\Users\shani\Documents\Personal-AI-Employee-FTEs\credentials.json
C:\Users\shani\Documents\Personal-AI-Employee-FTEs\token.json
```

The `token.json` file contains your OAuth token for future API calls.

---

## Step 4: Start Gmail Watcher

```bash
cd C:\Users\shani\Documents\Personal-AI-Employee-FTEs\AI_Employee_Vault\watchers
python3 gmail_watcher.py
```

**Expected output:**
```
Gmail Watcher v0.1.0
Vault: C:\Users\shani\Documents\Personal-AI-Employee-FTEs\AI_Employee_Vault
Credentials: ...\credentials.json
Query: is:unread is:important
Interval: 120s

Monitoring Gmail for unread/important emails...
Press Ctrl+C to stop.
```

---

## Step 5: Test with Real Email

1. Send yourself a test email from another account
2. Mark it as "Important" (star it)
3. Wait up to 2 minutes

**Expected:**
- Watcher detects the email
- Creates action file in `Needs_Action/`
- File named: `EMAIL_{subject}_{timestamp}.md`

---

## Configuration Options

### Custom Gmail Query

```bash
# Only emails from specific sender
python3 gmail_watcher.py --query "from:client@example.com is:unread"

# Emails with specific subject
python3 gmail_watcher.py --query "subject:invoice is:unread"

# All unread emails (not just important)
python3 gmail_watcher.py --query "is:unread"
```

### Custom Check Interval

```bash
# Check every 5 minutes (300 seconds)
python3 gmail_watcher.py --interval 300
```

### Full Example

```bash
python3 gmail_watcher.py \
  --vault-path "C:\Users\shani\Documents\Personal-AI-Employee-FTEs\AI_Employee_Vault" \
  --credentials "C:\Users\shani\Documents\Personal-AI-Employee-FTEs\credentials.json" \
  --interval 120 \
  --query "is:unread is:important"
```

---

## Troubleshooting

### Error: "Credentials file not found"

**Solution:**
```bash
# Verify file exists
dir C:\Users\shani\Documents\Personal-AI-Employee-FTEs\credentials.json

# Or specify full path
python3 gmail_watcher.py --authenticate --credentials "C:\full\path\to\credentials.json"
```

### Error: "Token expired"

**Solution:** Re-authenticate
```bash
python3 gmail_watcher.py --authenticate
```

### Error: "Gmail API not enabled"

**Solution:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project
3. Navigate to "APIs & Services" > "Library"
4. Search for "Gmail API"
5. Click "Enable"

### No Emails Detected

**Solutions:**
1. Check if emails are marked as "Important"
2. Try less restrictive query: `is:unread`
3. Check `gmail_processed_state.json` - emails may already be processed
4. Review logs: `Logs/watcher_YYYY-MM-DD.log`

---

## Action File Format

When an email is detected, creates:

```markdown
---
type: email
from: sender@example.com
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

{email_snippet}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
```

---

## Process Emails with Qwen

After Gmail Watcher creates action files:

```bash
cd C:\Users\shani\Documents\Personal-AI-Employee-FTEs\AI_Employee_Vault

# Process all pending emails
qwen "Check /Needs_Action and process all email items"

# Process with approval for sending replies
qwen "Process emails, draft replies, create approval requests for sends"
```

---

## Security Notes

- ✅ OAuth 2.0 authentication (no passwords stored)
- ✅ Token stored locally in `token.json`
- ✅ Read-only access by default
- ⚠️ Never commit `token.json` to version control
- ⚠️ Revoke access anytime from [Google Account](https://myaccount.google.com/permissions)

---

## Next Steps

After Gmail Watcher is working:

1. **Set up scheduled processing** - Use Task Scheduler
2. **Configure approval workflow** - For sending replies
3. **Create Email MCP** - To send emails via API
4. **Integrate with LinkedIn** - Cross-post business updates

---

*Gmail Watcher Setup Guide v0.1.0*
*Silver Tier - AI Employee Hackathon 0*
