---
name: task-scheduler
description: |
  Schedule recurring tasks and briefings via cron (Linux/Mac) or Task Scheduler (Windows).
  Use when the AI Employee needs to run automatically at specific times,
  such as daily briefings, weekly audits, or monthly reports.
---

# Task Scheduler Skill

Schedule recurring AI Employee tasks using system schedulers.

## Overview

The Task Scheduler is a **Silver Tier** AI Employee skill that:
- Schedules recurring Qwen Code commands
- Automates daily/weekly/monthly briefings
- Triggers periodic processing runs
- Enables unattended operation
- Supports cron (Linux/Mac) and Task Scheduler (Windows)

## Scheduling Options

| Platform | Scheduler | Command Format |
|----------|-----------|----------------|
| Linux/Mac | cron | `qwen "command"` |
| Windows | Task Scheduler | `qwen -p "command"` |
| All | Python schedule | `schedule.every().day.at("08:00")` |

## Scheduled Tasks

### Daily Briefing (8:00 AM)

Generates morning summary of pending items, recent activity, and priorities.

### Weekly Audit (Sunday 6:00 PM)

Reviews week's transactions, completed tasks, and generates CEO briefing.

### Hourly Processing

Checks Needs_Action folder and processes pending items.

### Monthly Report (1st of month, 9:00 AM)

Generates monthly summary, financial report, and goals review.

## Setup Instructions

### Linux/Mac (cron)

#### Step 1: Open crontab

```bash
crontab -e
```

#### Step 2: Add Scheduled Tasks

```bash
# Daily Briefing at 8:00 AM
0 8 * * * cd /path/to/AI_Employee_Vault && qwen "Generate daily briefing from Dashboard and recent activity" >> /tmp/ai_employee.log 2>&1

# Hourly processing
0 * * * * cd /path/to/AI_Employee_Vault && qwen -y "Process all files in Needs_Action, move completed to Done" >> /tmp/ai_employee.log 2>&1

# Weekly Audit - Sunday 6:00 PM
0 18 * * 0 cd /path/to/AI_Employee_Vault && qwen "Generate weekly audit report and CEO briefing" >> /tmp/ai_employee.log 2>&1

# Monthly Report - 1st of month at 9:00 AM
0 9 1 * * cd /path/to/AI_Employee_Vault && qwen "Generate monthly report and review Business_Goals.md progress" >> /tmp/ai_employee.log 2>&1
```

#### Step 3: Verify cron

```bash
crontab -l  # List scheduled tasks
grep CRON /var/log/syslog  # Check cron logs (Ubuntu/Debian)
```

### Windows (Task Scheduler)

#### Step 1: Open Task Scheduler

```bash
taskschd.msc
```

#### Step 2: Create Basic Task

1. **Action:** Create Basic Task
2. **Name:** AI Employee Daily Briefing
3. **Trigger:** Daily at 8:00 AM
4. **Action:** Start a program
5. **Program:** `qwen`
6. **Arguments:** `-p "Generate daily briefing from Dashboard and recent activity"`
7. **Start in:** `C:\Users\shani\Documents\Personal-AI-Employee-FTEs\AI_Employee_Vault`

#### Step 3: Using PowerShell Script

Create `scheduled_tasks.ps1`:

```powershell
# Daily Briefing
$action = New-ScheduledTaskAction -Execute "qwen" `
    -Argument "-p 'Generate daily briefing from Dashboard'" `
    -WorkingDirectory "C:\Users\shani\Documents\Personal-AI-Employee-FTEs\AI_Employee_Vault"

$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM

Register-ScheduledTask -TaskName "AI Employee Daily Briefing" `
    -Action $action -Trigger $trigger -User "shani"
```

Run as Administrator:
```powershell
powershell -ExecutionPolicy Bypass -File scheduled_tasks.ps1
```

### Python Schedule (Cross-Platform)

Create `scheduler.py`:

```python
import schedule
import subprocess
import time
from pathlib import Path

VAULT_PATH = Path(__file__).parent / "AI_Employee_Vault"

def run_qwen(command: str):
    """Run Qwen Code command."""
    subprocess.run(
        ["qwen", "-p", command],
        cwd=VAULT_PATH,
        capture_output=True
    )

# Schedule tasks
schedule.every().day.at("08:00").do(
    run_qwen, "Generate daily briefing from Dashboard and recent activity"
)

schedule.every().hour.do(
    run_qwen, "Process all files in Needs_Action, move completed to Done"
)

schedule.every().sunday.at("18:00").do(
    run_qwen, "Generate weekly audit report and CEO briefing"
)

schedule.every().month.do(
    run_qwen, "Generate monthly report and review Business_Goals.md progress"
)

# Run scheduler
while True:
    schedule.run_pending()
    time.sleep(60)
```

Run in background:
```bash
# Linux/Mac
nohup python scheduler.py &

# Windows
start /B python scheduler.py
```

## Task Templates

### Daily Briefing Template

```bash
qwen "Generate daily briefing including:
1. Items processed yesterday
2. Pending approvals
3. Today's priorities from Business_Goals.md
4. Any alerts or anomalies
Save to Briefings/DAILY_YYYY-MM-DD.md"
```

### Weekly Audit Template

```bash
qwen "Generate weekly audit including:
1. Revenue summary from Accounting
2. Completed tasks from Done folder
3. Bottleneck analysis
4. Subscription review
5. CEO Briefing with proactive suggestions
Save to Briefings/WEEKLY_YYYY-MM-DD.md"
```

### Monthly Report Template

```bash
qwen "Generate monthly report including:
1. Financial statements
2. Goal progress from Business_Goals.md
3. System performance metrics
4. Lessons learned
5. Next month priorities
Save to Briefings/MONTHLY_YYYY-MM.md"
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VAULT_PATH` | Path to Obsidian vault | Current dir |
| `LOG_FILE` | Path to scheduler log | scheduler.log |
| `QWEN_TIMEOUT` | Command timeout (seconds) | 300 |

### Error Handling

```python
# In scheduler script
try:
    run_qwen(command)
except subprocess.TimeoutExpired:
    log_error("Command timed out")
except Exception as e:
    log_error(f"Error: {e}")
    # Continue with next task
```

## Monitoring

### Check Task Status

**Linux/Mac:**
```bash
# View cron logs
grep CRON /var/log/syslog | tail -20

# Check if scheduler is running
ps aux | grep scheduler.py
```

**Windows:**
```powershell
# View Task Scheduler history
Get-ScheduledTask -TaskName "AI Employee*" | Get-ScheduledTaskInfo

# Check scheduler process
Get-Process python | Where-Object {$_.Path -like "*scheduler*"}
```

### Health Check Script

Create `health_check.py`:

```python
#!/usr/bin/env python3
"""Check if scheduled tasks are running."""

import subprocess
import sys

def check_cron():
    result = subprocess.run(["pgrep", "-f", "cron"], capture_output=True)
    return result.returncode == 0

def check_scheduler():
    result = subprocess.run(["pgrep", "-f", "scheduler.py"], capture_output=True)
    return result.returncode == 0

print("=== AI Employee Scheduler Health Check ===")
print(f"Cron daemon: {'✅ Running' if check_cron() else '❌ Stopped'}")
print(f"Scheduler: {'✅ Running' if check_scheduler() else '❌ Stopped'}")
```

## Troubleshooting

### Issue: Task Not Running

**Solutions:**
1. Check scheduler is running
2. Verify command path is correct
3. Check permissions
4. Review logs for errors

### Issue: Qwen Not Found

**Solutions:**
1. Use full path to qwen executable
2. Add to PATH in scheduler script
3. Activate virtual environment first

### Issue: Tasks Run But No Output

**Solutions:**
1. Check log file location
2. Verify vault path is correct
3. Ensure Qwen has file access

## Best Practices

1. **Log everything:** Capture stdout and stderr
2. **Set timeouts:** Prevent hung tasks
3. **Error handling:** Continue on failure
4. **Health checks:** Monitor scheduler status
5. **Test first:** Run commands manually before scheduling

## Related Skills

- **Plan Creator** - Schedule plan execution
- **Approval Workflow** - Schedule approval reminders
- **Gmail Watcher** - Schedule email processing

## Reference

- [cron documentation](https://man7.org/linux/man-pages/man5/crontab.5.html)
- [Windows Task Scheduler](https://docs.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
- [schedule library](https://schedule.readthedocs.io/)
- [Company Handbook](Company_Handbook.md)

---

*Task Scheduler Skill v0.1.0*
*Silver Tier - AI Employee Hackathon 0*
