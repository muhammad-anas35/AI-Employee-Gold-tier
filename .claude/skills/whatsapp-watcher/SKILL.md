---
name: whatsapp-watcher
description: |
  Monitor WhatsApp Web for urgent messages using Playwright automation. Detects messages with
  keywords like "urgent", "asap", "invoice", "payment", or "help" and creates action files.
  Use when you need to monitor WhatsApp for time-sensitive communications or integrate WhatsApp
  into automated workflows. Requires manual QR code setup.
---

# WhatsApp Watcher

Monitor WhatsApp Web for urgent messages containing specific keywords, automatically creating action files in the vault for immediate processing.

## Overview

This skill uses Playwright to automate WhatsApp Web, monitoring for urgent messages that contain keywords like "urgent", "asap", "invoice", "payment", or "help". When detected, it creates action files for Claude to process.

## Usage

```bash
# Start the WhatsApp watcher
python scripts/whatsapp_watcher.py

# Test mode (dry run)
python scripts/whatsapp_watcher.py --test

# Custom check interval (seconds)
python scripts/whatsapp_watcher.py --interval 30
```

## What It Does

1. **Monitors WhatsApp Web** using Playwright automation
2. **Scans unread chats** for urgent keywords
3. **Creates action files** in `/Needs_Action/WHATSAPP_*.md`
4. **Preserves session** for continuous monitoring
5. **Logs all activity** to `/Logs/whatsapp_watcher.log`

## Prerequisites

### Install Playwright

```bash
# Install Playwright
pip install playwright

# Install browser binaries
playwright install chromium
```

### First Run Setup

```bash
# First run will open WhatsApp Web for QR code scan
python scripts/whatsapp_watcher.py --setup

# Scan QR code with your phone
# Session will be saved for future runs
```

## Configuration

### Environment Variables

```bash
# .env file
WHATSAPP_SESSION_PATH=./whatsapp_session
VAULT_PATH=./AI_Employee_Vault
CHECK_INTERVAL=30  # seconds
HEADLESS=true  # Run browser in background
```

### Keyword Configuration

Default urgent keywords:
- `urgent`
- `asap`
- `invoice`
- `payment`
- `help`
- `emergency`
- `critical`

Customize in `whatsapp_watcher.py`:
```python
self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'custom_keyword']
```

## Action File Format

Created files follow this structure:

```markdown
---
type: whatsapp
from: Contact Name
phone: +1234567890
received: 2026-03-12T20:26:00Z
priority: high
status: pending
keywords_matched: urgent, payment
---

# WhatsApp Message Received

## Message Content

[Message text content]

## Suggested Actions

- [ ] Reply to sender
- [ ] Process request
- [ ] Create invoice/payment
- [ ] Archive after handling

## Contact Details

- **From:** Contact Name
- **Phone:** +1234567890
- **Time:** 2026-03-12 20:26:00
- **Keywords:** urgent, payment
- **Priority:** high

## Notes

Add processing notes here.
```

## Integration with Workflow

```
WhatsApp Message → WhatsApp Watcher → /Needs_Action/WHATSAPP_*.md
                                            ↓
                              Claude processes with /process-vault-tasks
                                            ↓
                              Creates plan or draft reply
                                            ↓
                              Requests approval if needed
                                            ↓
                              Human sends reply manually
                                            ↓
                              Marks as done, logs action
```

## Features

### Keyword Detection
- Scans message text for urgent keywords
- Case-insensitive matching
- Multiple keyword support
- Configurable keyword list

### Session Persistence
- Saves WhatsApp Web session
- No need to scan QR code every time
- Persistent across restarts
- Secure local storage

### Smart Filtering
- Only processes unread messages
- Ignores group messages (optional)
- Focuses on urgent communications
- Prevents duplicate processing

### Error Handling
- Graceful handling of connection issues
- Auto-reconnect on session loss
- Continues monitoring after errors
- Detailed error logging

## Security & Privacy

### Session Management
- Session stored locally in `whatsapp_session/`
- Never sync session to cloud
- Add to `.gitignore`
- Encrypted by Playwright

### Privacy
- Messages stay local
- No external logging
- Full audit trail locally
- Read-only access to chats

### WhatsApp Terms of Service
⚠️ **Important:** WhatsApp's Terms of Service prohibit automated access to WhatsApp Web. Use this tool:
- For personal use only
- At your own risk
- With awareness of potential account restrictions
- Consider official WhatsApp Business API for commercial use

## Monitoring

### Check Status

```bash
# View recent activity
tail -f AI_Employee_Vault/Logs/whatsapp_watcher.log

# Check created action files
ls -lt AI_Employee_Vault/Needs_Action/WHATSAPP_*.md

# View browser session
ls -la whatsapp_session/
```

### Health Checks

The watcher logs heartbeat messages:
```
2026-03-12 20:26:00 - WhatsAppWatcher - INFO - Checking for urgent messages...
2026-03-12 20:26:02 - WhatsAppWatcher - INFO - Found 1 urgent message(s)
2026-03-12 20:26:02 - WhatsAppWatcher - INFO - Created WHATSAPP_client_urgent_1710275162.md
```

## Troubleshooting

### "Session expired" error
```bash
# Delete session and re-authenticate
rm -rf whatsapp_session/
python scripts/whatsapp_watcher.py --setup
```

### "Browser not found" error
```bash
# Reinstall Playwright browsers
playwright install chromium
```

### No messages detected
- Check keyword configuration
- Verify messages are unread
- Check WhatsApp Web is logged in
- Review logs for errors

### High CPU usage
- Increase check interval
- Use headless mode
- Close unnecessary browser tabs

## Advanced Usage

### Custom Message Processing

Extend the watcher for custom logic:

```python
def should_process_message(self, message_text, contact_name):
    """Custom filtering logic"""
    # Only process from specific contacts
    if contact_name not in ['Important Client', 'Boss']:
        return False

    # Check for specific patterns
    if 'invoice' in message_text.lower():
        return True

    return False
```

### Group Message Handling

```python
# Enable group message monitoring
self.monitor_groups = True

# Filter specific groups
self.allowed_groups = ['Work Team', 'Client Group']
```

### Integration with Reply System

```bash
# Chain with processing and reply
python scripts/whatsapp_watcher.py &
sleep 5
claude /process-vault-tasks
# Human reviews and sends reply manually
```

## Performance

- **Memory:** ~200MB (Chromium browser)
- **CPU:** Low (only during checks)
- **Network:** Minimal (WhatsApp Web connection)
- **Disk:** ~100MB (browser session)

## Limitations

- Requires active internet connection
- WhatsApp Web must stay logged in
- Cannot send messages (read-only)
- Manual reply required
- Subject to WhatsApp's rate limits

## Dependencies

```
playwright==1.41.0
```

## Alternative: WhatsApp Business API

For production use, consider:
- [WhatsApp Business API](https://business.whatsapp.com/products/business-platform)
- Official API with send capabilities
- No automation restrictions
- Requires business verification
- Paid service

## See Also

- `/process-vault-tasks` - Process created action files
- `Company_Handbook.md` - WhatsApp handling rules
- `orchestrator.py` - Automated scheduling
- `gmail_watcher.py` - Similar pattern for email
