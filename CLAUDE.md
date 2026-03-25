# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal AI Employee - Silver Tier implementation for the "Building Autonomous FTEs in 2026" hackathon. This is an autonomous agent system that monitors Gmail, WhatsApp, and filesystem events, processes tasks using Claude Code reasoning, and executes actions with human-in-the-loop approval workflows.

**Status:** 100% Complete - Ready for demo video and submission
**Developer:** Muhammad Anas Asif
**Tier:** Silver (8/8 requirements met)

## Core Architecture

### The Brain: Claude Code + VaultManager
- `claude_integration.py` - VaultManager reads tasks from `/Needs_Action`, creates plans in `/Plans`, manages approval workflow
- Claude Code provides reasoning and generates action plans

### The Memory: Obsidian Vault
- `AI_Employee_Vault/` - Local-first Markdown vault (not yet created in this directory)
- Dashboard.md - Real-time metrics
- Company_Handbook.md - Rules and boundaries
- Folder structure: Needs_Action/ → Plans/ → Pending_Approval/ → Approved/ → Done/

### The Senses: Watchers (Python)
- `base_watcher.py` - Abstract base class for all watchers (156 lines)
- `.claude/skills/gmail-watcher/` - Gmail monitoring with OAuth2
- `.claude/skills/whatsapp-watcher/` - WhatsApp message detection
- `filesystem_watcher.py` - Drop folder monitoring

### The Hands: MCP Servers
- Playwright MCP - Browser automation for LinkedIn posting
- Filesystem MCP - Vault access

### Orchestrator
- `.claude/skills/orchestrator/` - Master coordinator that runs all watchers and calls Claude Code skills

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Install Playwright for browser automation
playwright install chromium

# Verify setup
python verify.py
```

### Testing Individual Components
```bash
# Test Gmail watcher
python .claude/skills/gmail-watcher/scripts/gmail_watcher.py --test

# Test email sending workflow
python .claude/skills/send-email/scripts/send_email.py \
  --to "test@example.com" \
  --subject "Test" \
  --body "Hello from AI Employee"

# Approve email (move to Approved folder)
mv AI_Employee_Vault/Pending_Approval/EMAIL_*.md AI_Employee_Vault/Approved/

# Send approved emails
python .claude/skills/send-email/scripts/send_email.py --send-approved

# Test LinkedIn poster
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --test

# Test filesystem watcher
python filesystem_watcher.py --test
```

### Playwright MCP Server
```bash
# Start server (required for LinkedIn posting)
bash browsing-with-playwright/scripts/start-server.sh

# Stop server
bash browsing-with-playwright/scripts/stop-server.sh

# Verify server is running
python browsing-with-playwright/scripts/verify.py
```

### Running the System
```bash
# Start orchestrator (runs all watchers + calls Claude Code)
python .claude/skills/orchestrator/scripts/orchestrator.py

# View logs
tail -f AI_Employee_Vault/Logs/orchestrator.log
```

## Key Design Patterns

### BaseWatcher Pattern
All watchers inherit from `base_watcher.py`:
- Standardized interface with `check()` method
- Built-in logging and error handling
- Consistent run loop pattern
- Prevents code duplication

### Retry Handler
`retry_handler.py` provides exponential backoff:
- `@with_retry` decorator for transient failures
- Distinguishes transient vs permanent errors
- Context manager support

### Rate Limiter
`rate_limiter.py` prevents API abuse:
- Sliding window algorithm
- Per-action type limits (email: 10/hour, LinkedIn: 3/hour)
- `@rate_limited` decorator
- Persistent state in `rate_limits.json`

### Approval Workflow
Human-in-the-loop for sensitive actions:
1. Watcher detects event → creates task in `/Needs_Action`
2. VaultManager reads task → creates plan in `/Plans`
3. Action request → `/Pending_Approval` (EMAIL_*.md, POST_*.md)
4. Human reviews and moves to `/Approved`
5. Executor sends/posts → moves to `/Done`

## Agent Skills Structure

All functionality is packaged as Agent Skills with SKILL.md frontmatter:
- `browsing-with-playwright/` - Browser automation via Playwright MCP
- `.claude/skills/gmail-watcher/` - Gmail monitoring
- `.claude/skills/whatsapp-watcher/` - WhatsApp monitoring
- `.claude/skills/linkedin-poster/` - LinkedIn automation
- `.claude/skills/send-email/` - Email sending
- `.claude/skills/orchestrator/` - Master coordinator
- `.claude/skills/process-vault-tasks/` - Task processing
- `.claude/skills/update-dashboard/` - Dashboard updates

## Configuration Files

### Environment Variables (.env)
- Gmail API credentials (OAuth2)
- Vault path and drop folder
- Rate limits and intervals
- Feature flags

### MCP Configuration (mcp_config.json)
- Filesystem MCP for vault access
- Playwright MCP for browser automation
- Copy to `~/.config/claude-code/mcp.json`

### Rate Limits (rate_limits.json)
- Email: 10/hour
- LinkedIn: 3/hour, 10/day
- Payments: 5/day

## Important Notes

### Security
- All credentials in `.env` (not committed)
- OAuth2 for Gmail (token.json exists and is valid)
- Human approval required for sensitive actions
- Complete audit trail in `/Logs`

### Error Handling
- Automatic retry with exponential backoff for transient failures
- Rate limiting prevents API quota exhaustion
- Graceful degradation when services unavailable
- All errors logged to vault

### Testing Before Submission
The project is 100% complete. Before creating demo video:
1. Test filesystem watcher with file drop
2. Test Gmail watcher (credentials already configured)
3. Test email sending with approval workflow
4. Test LinkedIn posting with Playwright
5. Verify orchestrator coordinates all components
6. Check Dashboard.md updates correctly

## Documentation

- `README.md` - Project overview and quick start
- `PROJECT_GUIDE.md` - Complete setup, testing, and demo script
- `PROJECT_STATUS.md` - Current status and next steps
- `SUBMISSION_READY.md` - Quick submission checklist
- `SILVER_TIER_COMPLIANCE_ANALYSIS.md` - Detailed compliance verification
- `FINAL_TEST_REPORT.md` - Test results (14/17 passed, Grade A+)

## Hackathon Submission

**Form:** https://forms.gle/JR9T1SJq5rmQyGkGA
**Tier:** Silver (8/8 requirements met)
**Status:** Ready for demo video and submission
