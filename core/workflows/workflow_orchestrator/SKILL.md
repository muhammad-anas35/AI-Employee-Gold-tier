---
name: workflow-orchestrator
description: Cross-domain workflow orchestration connecting email, social media, accounting, and file systems
---

# Workflow Orchestrator

Orchestrates complex workflows across multiple domains (email, social media, accounting, files).

## Features

- Cross-domain workflow automation
- Email → Invoice → Social Media workflows
- File → Email → Accounting workflows
- Unified dashboard updates
- Workflow templates
- Error recovery across domains

## Example Workflows

### 1. Client Invoice Workflow
```
Email (payment request)
  → Create invoice in Odoo
  → Send invoice via email
  → Post update on LinkedIn
  → Update dashboard
```

### 2. Content Publishing Workflow
```
File drop (blog post)
  → Post to LinkedIn
  → Post to Twitter
  → Post to Facebook
  → Send email notification
  → Update dashboard
```

### 3. Business Update Workflow
```
Odoo (new invoice paid)
  → Send thank you email
  → Post testimonial request
  → Update dashboard
```

## Usage

### Define workflow

```python
workflow = {
    "name": "client_invoice",
    "trigger": "email_received",
    "steps": [
        {"action": "create_invoice", "domain": "odoo"},
        {"action": "send_email", "domain": "gmail"},
        {"action": "post_update", "domain": "linkedin"}
    ]
}
```

### Execute workflow

```bash
python .claude/skills/workflow-orchestrator/scripts/workflow_orchestrator.py --workflow client_invoice
```

## Workflow Templates

Pre-built templates available:
- `client_invoice` - Invoice generation and notification
- `content_publish` - Multi-platform content publishing
- `payment_received` - Payment confirmation workflow
- `weekly_report` - Weekly business report distribution
