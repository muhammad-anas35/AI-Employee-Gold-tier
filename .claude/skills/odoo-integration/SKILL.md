---
name: odoo-integration
description: Integrate with Odoo accounting system for invoice generation, expense tracking, and financial reporting
---

# Odoo Integration Skill

This skill provides integration with Odoo Community Edition for accounting operations.

## Features
- Create customers
- Generate invoices
- Record expenses
- Track payments
- Generate financial reports
- Weekly accounting audit

## Prerequisites
- Odoo Community Edition 19+ running (Docker recommended)
- Accounting module installed
- Admin credentials configured

## Configuration

Add to `.env`:
```bash
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin@example.com
ODOO_PASSWORD=admin
```

## Usage

### Create Invoice
```bash
# Via Claude Code
claude /odoo-integration --create-invoice \
  --client "Client A" \
  --email "client@example.com" \
  --amount 1500 \
  --description "January 2026 Services"
```

### Record Expense
```bash
# Via Claude Code
claude /odoo-integration --record-expense \
  --category "Software" \
  --amount 99 \
  --description "Monthly subscription"
```

### Get Financial Summary
```bash
# Via Claude Code
claude /odoo-integration --financial-summary \
  --period "this-month"
```

## Integration with AI Employee

The Odoo integration automatically:
1. Creates invoices when requested via email/WhatsApp
2. Records expenses from bank transactions
3. Generates weekly financial reports
4. Provides data for CEO Briefing

## Approval Workflow

All financial actions require human approval:
- Invoice creation → `/Pending_Approval/`
- Expense recording → `/Pending_Approval/`
- Payment processing → `/Pending_Approval/`

## Audit Logging

All Odoo operations are logged to:
- `AI_Employee_Vault/Logs/YYYY-MM-DD.json`
- Includes: timestamp, action, actor, result

## Troubleshooting

### Odoo not accessible
```bash
# Check if Odoo is running
docker ps | grep odoo

# Restart Odoo
cd odoo-docker
docker-compose restart odoo
```

### Authentication failed
- Verify credentials in `.env`
- Check Odoo database name
- Ensure user has accounting permissions

### Invoice creation failed
- Verify customer exists
- Check accounting module is installed
- Review Odoo logs: `docker logs odoo`
