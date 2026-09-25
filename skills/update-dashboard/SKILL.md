# Update Dashboard

Automatically update the AI Employee Dashboard with real-time metrics and activity.

## Overview

This skill maintains the Dashboard.md file with current status, metrics, and recent activities.

## Usage

```bash
claude /update-dashboard --vault-path "path/to/AI_Employee_Vault" --metric "pending_tasks" --value 5
```

## What It Does

1. **Reads** current vault state
2. **Calculates** metrics (pending tasks, completed today, etc.)
3. **Updates** Dashboard.md with latest values
4. **Logs** all updates
5. **Maintains** activity history

## Metrics Tracked

| Metric | Source | Update Frequency |
|--------|--------|------------------|
| Tasks Pending | Count files in `/Needs_Action` | Real-time |
| Needs Action | Count files in `/Needs_Action` | Real-time |
| Pending Approval | Count files in `/Pending_Approval` | Real-time |
| Tasks Completed Today | Count files moved to `/Done` today | Real-time |
| Monthly Revenue | Sum from `/Accounting/` | Daily |
| Monthly Expenses | Sum from `/Accounting/` | Daily |
| Watchers Running | Check process status | Every 5 min |

## Dashboard Sections

### Executive Summary
Quick overview of system health and pending items.

### Key Metrics
Real-time counters and status indicators.

### Recent Activity
Timestamped log of recent actions (last 10).

### Active Projects
List of in-progress projects with deadlines.

### Alerts & Bottlenecks
Flagged issues requiring attention.

### Financial Summary
Revenue, expenses, and net balance.

### System Status
Health of watchers, Claude Code, vault sync.

## Example Update

```bash
# Update pending tasks count
claude /update-dashboard --metric "pending_tasks" --value 3

# Add activity log entry
claude /update-dashboard --activity "Processed invoice from Client A"

# Update financial metrics
claude /update-dashboard --metric "monthly_revenue" --value 5000
```

## Automatic Updates

The skill can be scheduled to run automatically:

```bash
# Every hour (cron)
0 * * * * claude /update-dashboard --auto

# Every 30 minutes (Windows Task Scheduler)
Every 30 minutes: claude /update-dashboard --auto
```

## Activity Logging

Recent activities are logged with timestamps:

```markdown
## 📋 Recent Activity

- **[2026-02-23 17:51]** Dashboard updated with metrics
- **[2026-02-23 17:45]** Task completed: Process invoice
- **[2026-02-23 17:30]** New file detected in drop folder
```

## Alert Triggers

The skill automatically flags alerts for:

- More than 5 pending tasks
- Approval requests older than 24 hours
- Failed watchers
- Vault sync issues
- Unusual financial activity

## Integration Points

- **claude_integration.py** - Python backend
- **filesystem_watcher.py** - File system events
- **Company_Handbook.md** - Rules and thresholds
- **Logs/** - Audit trail

## Configuration

```bash
export VAULT_PATH="/path/to/AI_Employee_Vault"
export ALERT_THRESHOLD_PENDING=5
export ALERT_THRESHOLD_APPROVAL_AGE=24  # hours
export AUTO_UPDATE_INTERVAL=3600  # seconds
```

## Error Handling

- If Dashboard.md is locked, retry after 5 seconds
- If metrics calculation fails, use cached values
- All errors logged to `/Logs/dashboard_updates.log`

## See Also

- Dashboard.md - The dashboard template
- Company_Handbook.md - Alert thresholds
- process-vault-tasks - Task processing skill
