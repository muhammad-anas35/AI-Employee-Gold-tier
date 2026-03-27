---
name: ralph-wiggum-loop
description: Autonomous task completion loop that continuously processes tasks from /Needs_Action without human intervention
---

# Ralph Wiggum Loop

The autonomous task completion loop - the heart of Gold tier autonomy.

## What It Does

Continuously monitors `/Needs_Action` folder and autonomously:
1. Reads pending tasks
2. Analyzes task requirements
3. Creates execution plans
4. Executes safe actions automatically
5. Requests approval for sensitive actions
6. Logs all activities
7. Self-heals on errors

## Features

- **Autonomous Operation:** Runs every 10 minutes
- **Smart Decision Making:** Knows what needs approval vs auto-execute
- **Self-Healing:** Recovers from errors automatically
- **Audit Trail:** Complete logging of all actions
- **Safety First:** Sensitive actions always require approval

## Usage

### Start the loop (recommended)

Use Claude Code's `/loop` command to run continuously:

```bash
/loop 10m python .claude/skills/ralph-wiggum-loop/scripts/ralph_loop.py
```

This will run the loop every 10 minutes automatically. Claude Code manages scheduling and restarts.

### Run once (test mode)

```bash
python .claude/skills/ralph-wiggum-loop/scripts/ralph_loop.py
```

### Stop the loop

Stop the `/loop` command in Claude Code interface.

## How It Works

```
Every 10 minutes:
  1. Check /Needs_Action for tasks
  2. For each task:
     - Read and analyze
     - Determine if safe to auto-execute
     - If safe: Execute and move to /Done
     - If sensitive: Create approval request in /Pending_Approval
     - If error: Retry with backoff, then move to /Needs_Action with error note
  3. Check /Approved for approved actions
  4. Execute approved actions
  5. Update dashboard with metrics
  6. Log all activities
```

## Auto-Execute vs Approval

**Auto-Execute (Safe):**
- Reading emails
- Creating drafts
- Organizing files
- Updating dashboard
- Generating reports
- Creating invoices (draft mode)

**Requires Approval (Sensitive):**
- Sending emails to new contacts
- Posting on social media
- Making payments
- Deleting files
- Finalizing invoices

## Safety Features

- Dry-run mode for testing
- Rate limiting (max 10 actions per cycle)
- Error recovery with exponential backoff
- Dead letter queue for failed tasks
- Health monitoring
- Emergency stop capability

## Monitoring

Check logs:
```bash
tail -f AI_Employee_Vault/Logs/ralph_loop.log
```

View metrics:
```bash
cat AI_Employee_Vault/Dashboard.md
```

## Configuration

Edit `ralph_loop_config.json`:
```json
{
  "interval_minutes": 10,
  "max_actions_per_cycle": 10,
  "auto_approve_safe_actions": true,
  "enable_self_healing": true,
  "max_retries": 3
}
```
