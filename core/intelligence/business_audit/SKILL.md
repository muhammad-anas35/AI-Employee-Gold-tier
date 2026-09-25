---
name: business-audit
description: Generate automated weekly business audit reports with metrics, insights, and recommendations
---

# Business Audit Skill

Automatically generates comprehensive weekly business audit reports analyzing all activities, metrics, and providing actionable insights.

## Features

- Weekly automated report generation
- Cross-domain activity analysis (email, social media, accounting, files)
- Key performance metrics tracking
- Trend analysis and insights
- Actionable recommendations
- Audit trail compliance
- Export to multiple formats (Markdown, PDF, JSON)

## Usage

### Generate weekly audit

```bash
python .claude/skills/business-audit/scripts/business_audit.py --generate
```

### Generate custom date range

```bash
python .claude/skills/business-audit/scripts/business_audit.py --from 2026-03-20 --to 2026-03-27
```

### Schedule weekly audits

```bash
# Run every Monday at 9 AM
python .claude/skills/business-audit/scripts/business_audit.py --schedule
```

## Report Sections

1. **Executive Summary**
   - Week overview
   - Key highlights
   - Critical issues

2. **Activity Metrics**
   - Emails processed
   - Tasks completed
   - Social media posts
   - Invoices generated
   - Files organized

3. **Performance Analysis**
   - Response times
   - Completion rates
   - Error rates
   - Approval workflow metrics

4. **Financial Summary**
   - Revenue (from Odoo)
   - Expenses
   - Outstanding invoices
   - Payment status

5. **Social Media Analytics**
   - Posts published
   - Engagement metrics
   - Platform breakdown

6. **Recommendations**
   - Process improvements
   - Bottleneck identification
   - Automation opportunities

## Output

Reports saved to:
- `AI_Employee_Vault/Reports/AUDIT_YYYY-MM-DD.md`
- `AI_Employee_Vault/Reports/AUDIT_YYYY-MM-DD.json`

## Scheduling

The audit runs automatically every Monday at 9 AM when scheduled. Manual runs can be triggered anytime.
