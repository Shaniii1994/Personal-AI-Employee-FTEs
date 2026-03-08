---
name: approval-workflow
description: |
  Human-in-the-loop approval workflow for sensitive actions.
  Use when AI needs human approval before sending emails, making payments,
  or taking other sensitive actions. Implements file-based approval pattern.
---

# Approval Workflow Skill

Human-in-the-loop approval system for sensitive AI actions.

## Overview

The Approval Workflow is a **Silver Tier** AI Employee skill that:
- Creates approval request files for sensitive actions
- Tracks approval status (pending/approved/rejected)
- Enables human review before action execution
- Maintains audit trail of all approvals
- Implements file-based handoff pattern

## When Approval is Required

Always create approval request for:

| Action Type | Threshold | Approval Required |
|-------------|-----------|-------------------|
| Email send | New recipient | ✅ Always |
| Email send | Bulk (>5 recipients) | ✅ Always |
| Payment | Any amount to new payee | ✅ Always |
| Payment | > $50 to existing payee | ✅ Always |
| Social post | Public posts | ✅ Always |
| File delete | Any deletion | ✅ Always |
| Calendar event | External meetings | ✅ Recommended |

## Approval File Format

```markdown
---
type: approval_request
id: APPROVAL_20260225_001
action: email_send
to: client@example.com
subject: Invoice #123
amount: 1500.00
created: 2026-02-25T10:30:00Z
expires: 2026-02-26T10:30:00Z
status: pending
created_by: qwen_code
---

# Approval Request: Send Email

## Action Details
- **Action:** Send Email
- **To:** client@example.com
- **Subject:** Invoice #123 - January 2026
- **Amount:** $1,500.00

## Email Content

```
Dear Client,

Please find attached your invoice for January 2026 services.

Amount Due: $1,500.00
Due Date: March 27, 2026

Thank you for your business.

Best regards,
AI Employee
```

## Attachments
- invoice_123.pdf

## Context
- Source: EMAIL_request_client.md
- Client has requested invoice via email
- Amount verified against Company_Handbook.md rates

## To Approve
Move this file to `/Approved` folder.

## To Reject
Move this file to `/Rejected` folder with reason.

## Expiration
This approval request expires on 2026-02-26T10:30:00Z.
After expiration, recreate if still needed.

---
*Created by ApprovalWorkflow v0.1.0*
```

## Folder Structure

```
AI_Employee_Vault/
├── Pending_Approval/     # Awaiting human decision
│   ├── APPROVAL_email_send_001.md
│   └── APPROVAL_payment_002.md
├── Approved/             # Ready for action
│   └── (moved from Pending_Approval)
├── Rejected/             # Declined actions
│   └── (moved from Pending_Approval)
└── Logs/
    └── approvals_YYYY-MM-DD.log
```

## Workflow

### 1. AI Creates Approval Request

```markdown
# Qwen detects sensitive action needed
# Creates: /Pending_Approval/APPROVAL_email_send_001.md
```

### 2. Human Reviews

```bash
# Human opens Pending_Approval folder
# Reads approval request
# Reviews action details
```

### 3. Human Decides

**To Approve:**
```bash
# Move file to /Approved
move Pending_Approval/APPROVAL_*.md Approved/
```

**To Reject:**
```bash
# Add rejection reason and move to /Rejected
# Edit file, add:
## Rejection Reason
Sent to wrong email address. Correct: correct@example.com

move Pending_Approval/APPROVAL_*.md Rejected/
```

### 4. AI Processes Approved Actions

```bash
# Qwen checks /Approved folder
# Executes approved actions
# Moves to /Done after completion
```

## Usage with Qwen

### Create Approval Request

```bash
qwen "Create approval request for sending invoice email to client@example.com. Include email content, attachment info, and context."
```

### Check Pending Approvals

```bash
qwen "List all pending approval requests and summarize what actions are waiting."
```

### Process Approved Actions

```bash
qwen "Check /Approved folder and execute all approved actions. Move completed items to /Done."
```

### Approval Status Report

```bash
qwen "Generate approval status report: pending count, approved today, rejected this week."
```

## Examples

### Example 1: Email Approval

**Trigger:** Need to send invoice

**Approval Created:**
```markdown
---
type: approval_request
action: email_send
to: client@company.com
---

# Approve: Send Invoice Email

**To:** client@company.com
**Subject:** Invoice #123
**Content:** [email body]
**Attachment:** invoice_123.pdf
```

**Human:** Moves to `/Approved`

**Qwen:** Sends email, moves to `/Done`

### Example 2: Payment Approval

**Trigger:** Need to pay vendor

**Approval Created:**
```markdown
---
type: approval_request
action: payment
amount: 500.00
recipient: Vendor LLC
---

# Approve: Payment to Vendor LLC

**Amount:** $500.00
**Recipient:** Vendor LLC (Bank: ****1234)
**Reason:** Invoice #V-456 payment
**Due:** 2026-02-28
```

**Human:** Reviews bank details, moves to `/Approved`

**Qwen:** Initiates payment via MCP, logs transaction

### Example 3: Bulk Email Approval

**Trigger:** Newsletter to clients

**Approval Created:**
```markdown
---
type: approval_request
action: email_send_bulk
recipients: 25
---

# Approve: Send Monthly Newsletter

**Recipients:** 25 clients
**Subject:** February 2026 Newsletter
**Content:** [newsletter body]
```

**Human:** Reviews recipient list, approves

**Qwen:** Sends in batches of 5, logs each send

## Configuration

### Approval Thresholds

Edit `Company_Handbook.md` to customize:

```markdown
## Payment Thresholds
| Action | Auto-Process | Require Approval |
|--------|--------------|------------------|
| New Payee | ❌ Never | Always |
| Recurring | < $50 | ≥ $50 |
| One-time | ❌ Never | Always |
```

### Expiration Settings

```python
# Default expiration (hours)
APPROVAL_EXPIRATION_HOURS = 24

# Urgent approvals (hours)
URGENT_EXPIRATION_HOURS = 4
```

## Best Practices

### For AI
1. **Always create approval** for sensitive actions
2. **Include full context** in approval request
3. **Set reasonable expiration** based on urgency
4. **Log all approval activity**
5. **Never bypass approval** workflow

### For Humans
1. **Review daily** check Pending_Approval folder
2. **Decide promptly** don't let approvals expire
3. **Add context** if rejecting (helps AI learn)
4. **Audit weekly** review Approved/Rejected folders

## Audit Logging

All approval actions logged:

```json
{
  "timestamp": "2026-02-25T10:30:00Z",
  "approval_id": "APPROVAL_20260225_001",
  "action_type": "email_send",
  "created_by": "qwen_code",
  "approved_by": "human_user",
  "decision": "approved",
  "decision_time": "2026-02-25T11:00:00Z",
  "execution_time": "2026-02-25T11:01:00Z",
  "result": "success"
}
```

## Related Skills

- **Email MCP** - Send emails after approval
- **Plan Creator** - Track approval steps in plans
- **Task Scheduler** - Schedule approval reminders

## Reference

- [Company Handbook](Company_Handbook.md) - Approval thresholds
- [Dashboard](Dashboard.md) - Approval status summary
- [Pending_Approval/](Pending_Approval/) - Pending requests
- [Approved/](Approved/) - Ready for action
- [Rejected/](Rejected/) - Declined requests

---

*Approval Workflow Skill v0.1.0*
*Silver Tier - AI Employee Hackathon 0*
