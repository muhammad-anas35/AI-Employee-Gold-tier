---
name: gmail-watcher
description: |
  Monitor Gmail inbox for important and unread emails using Gmail API. Automatically creates
  action files in /Needs_Action for Claude to process. Use when you need to detect and respond
  to important emails, create email-based workflows, or integrate email monitoring into the
  AI Employee system.
---

# Gmail Watcher

Monitor Gmail inbox for important and unread emails, automatically creating action files in the vault for Claude to process.

## Overview

This skill continuously monitors your Gmail inbox using the Gmail API, detecting important or unread emails and creating structured action files in `/Needs_Action` for processing.

## Usage

```bash
# Start the Gmail watcher
python scripts/gmail_watcher.py

# Test mode (dry run)
python scripts/gmail_watcher.py --test

# Custom check interval (seconds)
python scripts/gmail_watcher.py --interval 300
```

## What It Does

1. **Monitors Gmail** using Gmail API every 2 minutes (configurable)
2. **Filters** for unread and important emails
3. **Creates action files** in `/Needs_Action/EMAIL_*.md`
4. **Tracks processed** emails to avoid duplicates
5. **Logs all activity** to `/Logs/gmail_watcher.log`

## Prerequisites

### Gmail API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download credentials as `credentials.json`
6. Place in project root

### First Run Authentication

```bash
# First run will open browser for OAuth consent
python scripts/gmail_watcher.py

# This creates token.json for future runs
# Keep token.json secure and never commit it
```

## Configuration

### Environment Variables

```bash
# .env file
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_TOKEN_PATH=./token.json
VAULT_PATH=./AI_Employee_Vault
CHECK_INTERVAL=120  # seconds
```

### Gmail Query Filters

Default query: `is:unread is:important`

Customize in `gmail_watcher.py`:
```python
# Monitor specific labels
query = 'is:unread label:clients'

# Monitor from specific senders
query = 'is:unread from:important@client.com'

# Monitor with keywords
query = 'is:unread (invoice OR payment OR urgent)'
```

## Action File Format

Created files follow this structure:

```markdown
---
type: email
from: sender@example.com
subject: Invoice Request
received: 2026-03-12T20:23:44Z
priority: high
status: pending
message_id: abc123xyz
---

## Email Content

[Email snippet or full body]

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to accounting
- [ ] Create invoice
- [ ] Archive after processing

## Email Details

- **From:** sender@example.com
- **To:** you@example.com
- **Date:** 2026-03-12 20:23:44
- **Labels:** IMPORTANT, UNREAD
```

## Integration with Workflow

```
Gmail Inbox → Gmail Watcher → /Needs_Action/EMAIL_*.md
                                      ↓
                          Claude processes with /process-vault-tasks
                                      ↓
                          Creates plan or draft reply
                                      ↓
                          Requests approval if needed
                                      ↓
                          Sends reply via Email MCP
                                      ↓
                          Marks as done, logs action
```

## Features

### Duplicate Prevention
- Tracks processed message IDs in `.processed_emails`
- Skips already-processed emails
- Persists across restarts

### Priority Detection
- Marks emails with IMPORTANT label as high priority
- Detects urgent keywords in subject/body
- Flags time-sensitive requests

### Smart Filtering
- Ignores spam and promotional emails
- Focuses on actionable messages
- Respects Gmail's importance signals

### Error Handling
- Exponential backoff on API errors
- Graceful handling of network issues
- Continues monitoring after transient failures

## Monitoring

### Check Status

```bash
# View recent activity
tail -f AI_Employee_Vault/Logs/gmail_watcher.log

# Check processed emails count
wc -l .processed_emails

# View created action files
ls -lt AI_Employee_Vault/Needs_Action/EMAIL_*.md
```

### Health Checks

The watcher logs heartbeat messages every check cycle:
```
2026-03-12 20:23:44 - GmailWatcher - INFO - Checking for new emails...
2026-03-12 20:23:45 - GmailWatcher - INFO - Found 2 new emails
2026-03-12 20:23:45 - GmailWatcher - INFO - Created EMAIL_client_request_1710275025.md
```

## Security

### Credential Management
- OAuth2 tokens stored locally
- Never commit `credentials.json` or `token.json`
- Tokens auto-refresh when expired
- Scopes limited to read-only access

### Privacy
- Email content stays local
- No external logging or analytics
- Processed emails tracked by ID only
- Full audit trail in local logs

### Rate Limiting
- Respects Gmail API quotas
- Default: 1 check per 2 minutes
- Exponential backoff on rate limit errors

## Troubleshooting

### "Invalid credentials" error
```bash
# Delete token and re-authenticate
rm token.json
python scripts/gmail_watcher.py
```

### "API not enabled" error
- Enable Gmail API in Google Cloud Console
- Wait 1-2 minutes for propagation
- Retry

### No emails detected
- Check Gmail query filter
- Verify emails match criteria (unread + important)
- Check `.processed_emails` for duplicates

### Watcher stops running
- Check logs for errors
- Verify network connectivity
- Use process manager (PM2) for auto-restart

## Advanced Usage

### Custom Email Processing

Extend the watcher for custom logic:

```python
def should_process_email(self, message):
    """Custom filtering logic"""
    headers = self.get_headers(message)
    subject = headers.get('Subject', '').lower()

    # Only process invoices
    if 'invoice' not in subject:
        return False

    # Skip automated emails
    if 'noreply' in headers.get('From', ''):
        return False

    return True
```

### Integration with Other Skills

```bash
# Chain with processing
python scripts/gmail_watcher.py &
sleep 5
claude /process-vault-tasks

# Scheduled processing
# Add to cron:
# */5 * * * * cd /path/to/Silver && claude /process-vault-tasks
```

## Performance

- **Memory:** ~50MB per watcher instance
- **CPU:** Minimal (only during API calls)
- **Network:** ~1KB per check (no new emails)
- **Disk:** ~2KB per action file created

## Dependencies

```
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.116.0
```

## See Also

- `/process-vault-tasks` - Process created action files
- `/send-email` - Send email replies via MCP
- `Company_Handbook.md` - Email handling rules
- `orchestrator.py` - Automated scheduling
