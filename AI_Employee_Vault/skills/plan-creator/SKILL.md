---
name: plan-creator
description: |
  Create structured Plan.md files for complex multi-step tasks.
  Use when Qwen needs to break down complex tasks into actionable steps,
  track progress, and maintain visibility into ongoing work.
---

# Plan Creator Skill

Create structured Plan.md files for complex tasks that require multiple steps or coordination.

## Overview

The Plan Creator is a **Silver Tier** AI Employee skill that:
- Analyzes complex tasks from Needs_Action folder
- Creates structured Plan.md files with checkboxes
- Tracks progress on each step
- Provides visibility into ongoing work
- Enables resumption after interruptions

## When to Create Plans

Create a Plan.md when:
- Task requires 3+ steps
- Task spans multiple sessions
- Task requires approval at certain steps
- Task involves multiple files/folders
- Progress tracking is needed

## Plan.md Format

```markdown
---
type: plan
created: 2026-02-25T10:30:00Z
status: in_progress
priority: high
source: EMAIL_12345.md
estimated_steps: 5
completed_steps: 2
---

# Plan: Process Client Invoice Request

## Objective
Generate and send invoice to Client A for January 2026 services.

## Context
- Source: Email from client@example.com
- Subject: Invoice Request
- Amount: $1,500
- Due: Net 30

## Steps

- [x] Identify client details
- [x] Calculate amount owed
- [ ] Generate invoice PDF
- [ ] Send invoice via email (REQUIRES APPROVAL)
- [ ] Log transaction in Accounting
- [ ] Move to Done folder

## Current Status
**Step 3 of 6:** Generating invoice PDF

## Blockers
None

## Notes
- Client prefers PDF format
- Include payment terms: Net 30
- CC: accounting@mycompany.com

---
*Created by PlanCreator v0.1.0*
```

## Usage

### Creating a Plan with Qwen

```bash
# Create plan for complex task
qwen "Create a Plan.md for processing the invoice request in Needs_Action. Break down into steps, track progress, and identify any approvals needed."

# Update existing plan
qwen "Update PLAN_invoice_client_a.md with progress. Mark completed steps and identify next action."

# Resume interrupted task
qwen "Read PLAN_invoice_client_a.md and continue from where we left off."
```

### Plan Workflow

1. **Create:** Qwen creates Plan.md when detecting complex task
2. **Execute:** Work through steps, checking off completed items
3. **Update:** Update status and current step after each action
4. **Complete:** Mark all steps done, move to Done folder

## Integration with Approval Workflow

For steps requiring approval:

```markdown
## Steps

- [x] Draft email response
- [ ] Send email → **PENDING APPROVAL**
      See: /Pending_Approval/EMAIL_response_client_a.md

## Approval Status
Waiting for human approval to send email.
Move approval file from /Pending_Approval to /Approved to proceed.
```

## Examples

### Example 1: Invoice Processing Plan

**Trigger:** Email requesting invoice

**Plan Created:**
```markdown
---
type: plan
source: EMAIL_invoice_request.md
status: in_progress
---

# Plan: Process Invoice Request

## Steps
- [x] Extract client info from email
- [x] Look up rates in Company_Handbook.md
- [ ] Generate invoice PDF
- [ ] Create approval request
- [ ] Send invoice after approval
- [ ] Log in Accounting
```

### Example 2: Email Triage Plan

**Trigger:** Multiple important emails

**Plan Created:**
```markdown
---
type: plan
source: Multiple emails
status: in_progress
---

# Plan: Daily Email Triage

## Steps
- [x] Read all unread emails
- [x] Categorize by urgency
- [ ] Draft responses for urgent (3 emails)
- [ ] Schedule responses for normal (5 emails)
- [ ] Archive processed emails
```

### Example 3: Client Onboarding Plan

**Trigger:** New client signup

**Plan Created:**
```markdown
---
type: plan
source: FILEDROP_signup_form.pdf
status: in_progress
---

# Plan: Onboard New Client

## Steps
- [x] Extract client information
- [ ] Create client folder
- [ ] Send welcome email (APPROVAL NEEDED)
- [ ] Schedule kickoff meeting
- [ ] Set up billing
- [ ] Add to CRM
```

## Best Practices

### Plan Structure
1. **Clear objective:** One sentence describing goal
2. **Context section:** Background information
3. **Numbered steps:** Sequential, actionable items
4. **Status tracking:** Current step and progress
5. **Blockers section:** What's preventing progress

### When Updating Plans
1. Check off completed steps immediately
2. Update `completed_steps` count in frontmatter
3. Note current status
4. Document any blockers
5. Add relevant notes

### Plan Completion
1. Verify all steps are checked
2. Move source files to Done
3. Move Plan.md to Done
4. Update Dashboard.md

## Qwen Prompts

### Create Plan
```
Create a Plan.md for this task. Include:
- Clear objective
- All required steps as checkboxes
- Approval requirements
- Current status section
```

### Update Plan
```
Update PLAN_[name].md:
- Mark completed steps
- Update progress count
- Note current step
- Document any blockers
```

### Resume Plan
```
Read PLAN_[name].md and continue from step X.
Complete the next pending step.
```

## Related Skills

- **Approval Workflow** - Human-in-the-loop for sensitive steps
- **Gmail Watcher** - Creates plans for email tasks
- **WhatsApp Watcher** - Creates plans for urgent messages
- **Task Scheduler** - Schedule plan execution

## Reference

- [Company Handbook](Company_Handbook.md) - Rules for when to create plans
- [Dashboard](Dashboard.md) - Track active plans
- [Pending_Approval/](Pending_Approval/) - Approval requests from plans

---

*Plan Creator Skill v0.1.0*
*Silver Tier - AI Employee Hackathon 0*
