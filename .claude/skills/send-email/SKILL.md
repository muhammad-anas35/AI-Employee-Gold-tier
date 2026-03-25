---
name: send-email
description: |
  Send emails via Gmail API with approval workflow and audit logging. Smart approval logic
  determines if emails need human review based on recipient, content, and attachments. Use
  when you need to send emails programmatically, automate email responses, or integrate email
  sending into workflows. Supports attachments and templates.
---

# Send Email

Send emails via Gmail API with approval workflow and audit logging.

## Overview

This skill enables Claude to send emails through Gmail API with human-in-the-loop approval for sensitive communications. All emails are logged and tracked for audit purposes.

## Usage

```bash
# Send email with approval
claude /send-email --to "client@example.com" --subject "Invoice" --body "Please find attached..."

# Send to known contact (may auto-approve based on rules)
claude /send-email --to "known@client.com" --subject "Follow-up" --body "..."

# Send with attachment
claude /send-email --to "client@example.com" --subject "Report" --body "..." --attach "report.pdf"
```

## What It Does

1. **Creates email draft** in `/Plans/EMAIL_*.md`
2. **Checks approval rules** from Company_Handbook.md
3. **Requests approval** if needed via `/Pending_Approval/`
4. **Sends email** via Gmail API after approval
5. **Logs transaction** to `/Logs/` and moves to `/Done/`

## Prerequisites

### Gmail API Setup

Same as Gmail Watcher:
1. Enable Gmail API in Google Cloud Console
2. Create OAuth2 credentials
3. Download `credentials.json`
4. Authenticate on first run

### Required Scopes

```python
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose'
]
```

## Configuration

### Environment Variables

```bash
# .env file
GMAIL_CREDENTIALS_PATH=./credentials.json
GMAIL_TOKEN_PATH=./token.json
VAULT_PATH=./AI_Employee_Vault
```

### Approval Rules

From `Company_Handbook.md`:

**Auto-approve:**
- Replies to known contacts
- Follow-up emails
- Routine communications

**Always require approval:**
- New contacts
- Bulk emails (>5 recipients)
- Emails with attachments
- Sensitive content

## Email Draft Format

### Pending Approval

```markdown
---
type: email_send
to: client@example.com
subject: Invoice #2026-001
status: pending_approval
created: 2026-03-12T20:30:00Z
priority: medium
---

# Email Send Request

## Email Details

- **To:** client@example.com
- **Subject:** Invoice #2026-001
- **Attachments:** invoice_2026_001.pdf

## Email Body

Dear Client,

Please find attached your invoice for March 2026.

Payment is due within 30 days.

Best regards,
Your Company

## Approval Required

This email is to a known contact but includes an attachment.

**To Approve:** Move to `/Approved/`
**To Reject:** Move to `/Rejected/`

## Notes

Add any modifications or notes here.
```

## Workflow

```
Email Request → Draft Created → Check Rules
                                    ↓
                        Known Contact? → Auto-send
                                    ↓
                        New/Sensitive? → /Pending_Approval/
                                    ↓
                              Human Reviews
                                    ↓
                              Moves to /Approved/
                                    ↓
                              Gmail API sends
                                    ↓
                              Logs & moves to /Done/
```

## Features

### Smart Approval Logic

```python
def requires_approval(to_email, subject, body, attachments):
    """Determine if email needs approval"""

    # Check if known contact
    if is_known_contact(to_email):
        # Known contact with no attachment = auto-approve
        if not attachments:
            return False

    # New contact always requires approval
    if not is_known_contact(to_email):
        return True

    # Bulk email requires approval
    if ',' in to_email or ';' in to_email:
        return True

    # Sensitive keywords require approval
    sensitive_keywords = ['payment', 'invoice', 'contract', 'legal']
    if any(kw in subject.lower() or kw in body.lower() for kw in sensitive_keywords):
        return True

    return False
```

### Known Contacts Database

Maintained in `AI_Employee_Vault/known_contacts.json`:

```json
{
  "contacts": [
    {
      "email": "client@example.com",
      "name": "Client Name",
      "added": "2026-03-01",
      "last_contact": "2026-03-12",
      "auto_approve": true
    }
  ]
}
```

### Email Templates

```markdown
# templates/invoice_email.md
---
type: email_template
category: invoice
---

Dear {{client_name}},

Please find attached your invoice #{{invoice_number}} for {{month}} {{year}}.

Amount due: ${{amount}}
Due date: {{due_date}}

Thank you for your business!

Best regards,
{{company_name}}
```

### Attachment Handling

```python
# Attach file from vault
claude /send-email \
  --to "client@example.com" \
  --subject "Invoice" \
  --template "invoice_email" \
  --attach "AI_Employee_Vault/Accounting/invoice_001.pdf"
```

## Security

### Credential Management
- OAuth2 tokens stored locally
- Automatic token refresh
- Never commit credentials
- Scoped permissions (send only)

### Audit Trail
Every email logged with:
- Timestamp
- Recipient(s)
- Subject
- Approval status
- Send result
- Message ID

### Rate Limiting
- Gmail API: 100 emails/day (free tier)
- 500 emails/day (workspace)
- Automatic backoff on limits

### Spam Prevention
- Max 10 emails per hour
- Max 5 recipients per email
- Cooldown between bulk sends
- Blacklist for bounced addresses

## Monitoring

### Check Status

```bash
# View pending emails
ls -lt AI_Employee_Vault/Pending_Approval/EMAIL_*.md

# View sent emails
ls -lt AI_Employee_Vault/Done/EMAIL_*.md

# Check send logs
cat AI_Employee_Vault/Logs/2026-03-12.json | jq '.[] | select(.action_type=="email_sent")'
```

### Email Metrics

Track in dashboard:
- Emails sent today
- Pending approvals
- Bounce rate
- Response rate

## Troubleshooting

### "Authentication failed"
```bash
# Delete token and re-authenticate
rm token.json
python scripts/send_email.py --auth
```

### "Quota exceeded"
- Check Gmail API quotas
- Wait 24 hours for reset
- Upgrade to workspace account

### Email not sending
- Check approval status
- Verify recipient email
- Check Gmail API logs
- Verify internet connection

### Emails going to spam
- Verify SPF/DKIM records
- Avoid spam trigger words
- Don't send too many at once
- Warm up new accounts

## Advanced Usage

### Bulk Email with Approval

```python
# Create bulk email request
claude /send-email \
  --to-list "clients.csv" \
  --subject "Monthly Newsletter" \
  --template "newsletter" \
  --require-approval
```

### Email Scheduling

```python
# Schedule email for later
claude /send-email \
  --to "client@example.com" \
  --subject "Follow-up" \
  --body "..." \
  --schedule "2026-03-13 09:00"
```

### Reply to Thread

```python
# Reply to existing email
claude /send-email \
  --reply-to "message_id_123" \
  --body "Thank you for your email..."
```

### Email Tracking

```python
# Track email opens (requires tracking pixel)
claude /send-email \
  --to "client@example.com" \
  --subject "Proposal" \
  --body "..." \
  --track-opens
```

## Integration with Workflow

### Auto-reply to Gmail Watcher

```
Gmail Watcher detects email → /Needs_Action/EMAIL_*.md
                                      ↓
                          Claude analyzes & drafts reply
                                      ↓
                          Creates /Plans/EMAIL_REPLY_*.md
                                      ↓
                          Requests approval
                                      ↓
                          Human approves
                                      ↓
                          Send Email skill sends reply
                                      ↓
                          Logs & marks original as done
```

## Performance

- **Latency:** 1-3 seconds per email
- **Memory:** ~50MB
- **Rate:** 1 email per second (safe)
- **Quota:** 100/day (free), 500/day (workspace)

## Dependencies

```
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.116.0
```

## See Also

- `gmail_watcher.py` - Receive emails
- `/process-vault-tasks` - Process email requests
- `Company_Handbook.md` - Email approval rules
- `orchestrator.py` - Automated email processing
