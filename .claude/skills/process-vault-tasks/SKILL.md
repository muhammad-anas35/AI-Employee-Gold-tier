# Process Vault Tasks

Process tasks from the AI Employee vault's Needs_Action folder and create action plans.

## Overview

This skill reads pending tasks from the vault, analyzes them, creates plans, and manages the task workflow.

## Usage

```bash
claude /process-vault-tasks --vault-path "path/to/AI_Employee_Vault"
```

## What It Does

1. **Scans** `/Needs_Action` folder for new tasks
2. **Analyzes** each task to understand requirements
3. **Creates** a plan in `/Plans` folder
4. **Requests approval** for sensitive actions
5. **Updates** Dashboard.md with progress
6. **Moves** completed tasks to `/Done`

## Task Workflow

```
Needs_Action → Analysis → Plan → Approval → Execution → Done
```

## Example Task Processing

### Input (Needs_Action/FILE_invoice_123.md)
```markdown
---
type: file_drop
original_name: invoice.pdf
---

# File Drop Detected

A new invoice file has been dropped for processing.
```

### Output (Plans/PLAN_invoice_processing_123.md)
```markdown
---
created: 2026-02-23T17:51:14Z
status: pending
---

# Plan: Process Invoice

## Steps
- [ ] Extract invoice details
- [ ] Log transaction
- [ ] Update accounting
- [ ] Archive file
```

## Approval Workflow

For sensitive actions, the skill creates approval requests:

```markdown
---
type: approval_request
action: payment
---

# Approval Required: Payment

Move to `/Approved` to proceed.
```

## Integration with Claude Code

The skill integrates with Claude Code's file system tools:

- **Read**: Access vault files
- **Write**: Create plans and logs
- **Move**: Organize files between folders

## Configuration

Set these environment variables:

```bash
export VAULT_PATH="/path/to/AI_Employee_Vault"
export LOG_LEVEL="INFO"
export AUTO_APPROVE_THRESHOLD=50  # Auto-approve actions under $50
```

## Error Handling

- Invalid task files are logged but don't stop processing
- Failed approvals are retried up to 3 times
- All errors are logged to `/Logs/`

## See Also

- Company_Handbook.md - Rules and boundaries
- Dashboard.md - Real-time status
- claude_integration.py - Python integration module
