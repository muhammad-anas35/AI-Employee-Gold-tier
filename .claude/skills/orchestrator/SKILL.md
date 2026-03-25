---
name: orchestrator
description: |
  Master process that coordinates all watchers, processes approvals, triggers Claude Code, and
  manages the overall AI Employee workflow. Handles health monitoring, auto-restart, scheduling,
  and approval processing. Use when you need to run the complete AI Employee system with all
  watchers and automated workflows.
---

# Orchestrator

Master process that coordinates all watchers, processes approvals, triggers Claude Code, and manages the overall AI Employee workflow.

## Overview

The Orchestrator is the central nervous system of your AI Employee. It manages all background processes, schedules tasks, monitors health, and ensures smooth operation of the entire system.

## Usage

```bash
# Start the orchestrator (runs all watchers)
python scripts/orchestrator.py

# Start with specific watchers only
python scripts/orchestrator.py --watchers gmail,filesystem

# Run in daemon mode (background)
python scripts/orchestrator.py --daemon

# Check status
python scripts/orchestrator.py --status
```

## What It Does

1. **Manages all watchers** (Gmail, WhatsApp, filesystem)
2. **Monitors process health** and auto-restarts failures
3. **Schedules periodic tasks** (dashboard updates, processing)
4. **Processes approval workflow** (moves approved items)
5. **Triggers Claude Code** at appropriate times
6. **Logs all orchestration events**

## Architecture

```
Orchestrator (Master Process)
├── Watcher Manager
│   ├── Gmail Watcher
│   ├── WhatsApp Watcher
│   └── Filesystem Watcher
├── Scheduler
│   ├── Periodic task processing
│   ├── Dashboard updates
│   └── Approval checks
├── Health Monitor
│   ├── Process watchdog
│   ├── Auto-restart
│   └── Alert on failures
└── Approval Processor
    ├── Check /Approved folder
    ├── Execute actions
    └── Move to /Done
```

## Configuration

### Environment Variables

```bash
# .env file
VAULT_PATH=./AI_Employee_Vault
ORCHESTRATOR_CHECK_INTERVAL=60  # seconds
ENABLE_GMAIL_WATCHER=true
ENABLE_WHATSAPP_WATCHER=true
ENABLE_FILESYSTEM_WATCHER=true
CLAUDE_PROCESS_INTERVAL=300  # 5 minutes
DASHBOARD_UPDATE_INTERVAL=1800  # 30 minutes
```

### Orchestrator Config

```json
// orchestrator_config.json
{
  "watchers": {
    "gmail": {
      "enabled": true,
      "check_interval": 120,
      "auto_restart": true
    },
    "whatsapp": {
      "enabled": true,
      "check_interval": 30,
      "auto_restart": true
    },
    "filesystem": {
      "enabled": true,
      "check_interval": 5,
      "auto_restart": true
    }
  },
  "scheduler": {
    "process_tasks": "*/5 * * * *",
    "update_dashboard": "*/30 * * * *",
    "check_approvals": "* * * * *",
    "daily_briefing": "0 8 * * *"
  },
  "health_monitor": {
    "check_interval": 60,
    "restart_delay": 5,
    "max_restarts": 3
  }
}
```

## Features

### Process Management

```python
# Start all watchers
orchestrator.start_watchers()

# Stop specific watcher
orchestrator.stop_watcher('gmail')

# Restart crashed watcher
orchestrator.restart_watcher('whatsapp')

# Get watcher status
status = orchestrator.get_status()
```

### Scheduling

```python
# Schedule periodic tasks
orchestrator.schedule_task(
    name="process_vault_tasks",
    command="claude /process-vault-tasks",
    cron="*/5 * * * *"  # Every 5 minutes
)

# Schedule dashboard update
orchestrator.schedule_task(
    name="update_dashboard",
    command="claude /update-dashboard",
    cron="*/30 * * * *"  # Every 30 minutes
)
```

### Approval Processing

```python
# Check for approved items
approved_items = orchestrator.check_approved_folder()

# Process each approved item
for item in approved_items:
    if item.type == "email":
        orchestrator.send_email(item)
    elif item.type == "linkedin_post":
        orchestrator.post_linkedin(item)
    elif item.type == "payment":
        orchestrator.process_payment(item)
```

### Health Monitoring

```python
# Check if watcher is running
if not orchestrator.is_running('gmail_watcher'):
    orchestrator.restart_watcher('gmail_watcher')
    orchestrator.alert_human("Gmail watcher restarted")

# Monitor resource usage
if orchestrator.get_memory_usage() > 1000:  # MB
    orchestrator.alert_human("High memory usage")
```

## Workflow

### Startup Sequence

```
1. Load configuration
2. Initialize vault structure
3. Start health monitor
4. Start all enabled watchers
5. Initialize scheduler
6. Begin orchestration loop
```

### Main Loop

```
Every minute:
1. Check watcher health
2. Process scheduled tasks
3. Check /Approved folder
4. Execute approved actions
5. Update metrics
6. Log status
```

### Shutdown Sequence

```
1. Stop accepting new tasks
2. Finish current tasks
3. Stop all watchers gracefully
4. Save state
5. Log shutdown
```

## Monitoring

### Status Dashboard

```bash
# View orchestrator status
python scripts/orchestrator.py --status

# Output:
# Orchestrator Status
# ==================
# Status: Running
# Uptime: 2h 34m
#
# Watchers:
# - Gmail: Running (PID: 1234)
# - WhatsApp: Running (PID: 1235)
# - Filesystem: Running (PID: 1236)
#
# Tasks Processed: 45
# Approvals Pending: 2
# Last Error: None
```

### Logs

```bash
# View orchestrator logs
tail -f AI_Employee_Vault/Logs/orchestrator.log

# View specific watcher logs
tail -f AI_Employee_Vault/Logs/gmail_watcher.log
```

### Metrics

Tracked in `AI_Employee_Vault/Logs/orchestrator_metrics.json`:

```json
{
  "timestamp": "2026-03-12T20:33:00Z",
  "uptime_seconds": 9240,
  "watchers_running": 3,
  "tasks_processed_today": 45,
  "approvals_pending": 2,
  "emails_sent_today": 12,
  "posts_published_today": 2,
  "errors_today": 0
}
```

## Error Handling

### Auto-Restart Logic

```python
# Watcher crashes
if watcher_crashed:
    restart_count = get_restart_count(watcher)

    if restart_count < MAX_RESTARTS:
        wait_time = 2 ** restart_count  # Exponential backoff
        time.sleep(wait_time)
        restart_watcher(watcher)
        log_restart(watcher, restart_count + 1)
    else:
        alert_human(f"{watcher} failed {MAX_RESTARTS} times")
        disable_watcher(watcher)
```

### Graceful Degradation

- Gmail watcher down → Continue with WhatsApp and filesystem
- Claude Code unavailable → Queue tasks for later
- Disk full → Alert human, pause watchers
- Network down → Retry with exponential backoff

## Security

### Process Isolation
- Each watcher runs in separate process
- Crashes don't affect other components
- Resource limits per process

### Credential Management
- Orchestrator doesn't store credentials
- Passes environment to child processes
- Credentials stay in .env file

### Audit Trail
- All orchestrator actions logged
- Process starts/stops recorded
- Approval executions tracked
- Error events logged

## Advanced Usage

### Custom Schedules

```python
# Add custom scheduled task
orchestrator.add_schedule(
    name="weekly_report",
    command="claude /generate-weekly-report",
    cron="0 8 * * 1"  # Monday 8 AM
)
```

### Conditional Processing

```python
# Only process if conditions met
if orchestrator.get_pending_count() > 10:
    orchestrator.trigger_claude_processing()
```

### Priority Queue

```python
# Process high-priority items first
orchestrator.process_by_priority([
    "urgent",
    "high",
    "medium",
    "low"
])
```

## Performance

- **Memory:** ~100MB base + watchers
- **CPU:** <5% average
- **Startup time:** 5-10 seconds
- **Shutdown time:** 2-5 seconds

## Troubleshooting

### Orchestrator won't start
```bash
# Check for existing instance
ps aux | grep orchestrator

# Kill existing instance
pkill -f orchestrator.py

# Check logs
tail -50 AI_Employee_Vault/Logs/orchestrator.log
```

### Watchers not starting
- Check watcher scripts exist
- Verify Python dependencies
- Check file permissions
- Review watcher logs

### High CPU usage
- Reduce check intervals
- Disable unused watchers
- Check for infinite loops
- Review error logs

### Tasks not processing
- Verify Claude Code is installed
- Check vault permissions
- Review scheduler configuration
- Check for errors in logs

## Production Deployment

### Using PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Start orchestrator
pm2 start orchestrator.py --interpreter python3 --name ai-employee

# Save configuration
pm2 save

# Auto-start on boot
pm2 startup
```

### Using systemd (Linux)

```ini
# /etc/systemd/system/ai-employee.service
[Unit]
Description=AI Employee Orchestrator
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/Silver
ExecStart=/usr/bin/python3 orchestrator.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable ai-employee
sudo systemctl start ai-employee
sudo systemctl status ai-employee
```

### Using Windows Task Scheduler

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: At startup
4. Action: Start program
5. Program: `python.exe`
6. Arguments: `orchestrator.py`
7. Start in: `D:\Coding world\Hackathone_0\Silver`

## Dependencies

```
watchdog==4.0.0
python-dotenv==1.0.0
schedule==1.2.0
psutil==5.9.0
```

## See Also

- `gmail_watcher.py` - Gmail monitoring
- `whatsapp_watcher.py` - WhatsApp monitoring
- `filesystem_watcher.py` - File monitoring
- `send_email.py` - Email sending
- `linkedin_poster.py` - LinkedIn posting
- `Company_Handbook.md` - Orchestration rules
