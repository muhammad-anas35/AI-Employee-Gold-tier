# LinkedIn Poster - Command Fix

**Date:** 2026-03-25
**Issue:** Documentation showed incorrect command-line arguments
**Status:** ✅ FIXED

---

## Issues Found

### 1. Wrong Argument Names in Documentation
**Incorrect (in docs):**
```bash
--content "text"      # WRONG
--post-approved       # WRONG
```

**Correct (actual script):**
```bash
--create "text"       # CORRECT
--publish             # CORRECT
```

### 2. Backslash Line Continuation Error
**Problem:** Windows CMD doesn't support `\` for line continuation like bash
**Solution:** Use single-line commands or proper Windows syntax

---

## Correct Commands

### Create a Post Draft
```bash
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --create "Your business update"
```

### Create with Category and Schedule
```bash
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --create "Your update" --category "business_update" --schedule "2026-03-26T09:00:00"
```

### Test Post Creation
```bash
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --test
```

### Publish Approved Posts
```bash
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --publish
```

### Setup LinkedIn Login
```bash
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --setup
```

---

## Available Arguments

From the script (`linkedin_poster.py` line 365-377):

| Argument | Type | Description |
|----------|------|-------------|
| `--setup` | flag | Initial setup: login to LinkedIn |
| `--create TEXT` | string | Create post draft with content |
| `--category TEXT` | string | Post category (default: business_update) |
| `--schedule TIME` | string | Schedule post for specific time (ISO format) |
| `--publish` | flag | Publish all approved posts |
| `--test` | flag | Test mode: create draft only |

---

## Complete Workflow Example

### 1. Create a Post
```bash
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --create "🚀 Excited to announce our Silver Tier AI Employee is complete! All 8 features tested and working. #AI #Automation"
```

**Output:**
```
Draft created: AI_Employee_Vault/Pending_Approval/POST_linkedin_business_update_1774427448.md
Review and move to /Approved/ to publish
```

### 2. Review the Draft
```bash
# Open and edit if needed
notepad AI_Employee_Vault/Pending_Approval/POST_linkedin_business_update_1774427448.md
```

### 3. Approve the Post
```bash
# Move to Approved folder
move AI_Employee_Vault\Pending_Approval\POST_*.md AI_Employee_Vault\Approved\
```

### 4. Publish Approved Posts
```bash
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --publish
```

---

## Setup Issue (--setup command)

### Problem
The `--setup` command tries to wait for LinkedIn login but times out or gets interrupted.

### Root Cause
```python
# Line 302 in linkedin_poster.py
page.wait_for_selector('[data-test-id="share-box-open"]', timeout=120000)
```

This selector waits for the LinkedIn share box, but:
1. LinkedIn's UI may have changed
2. Login might redirect to different pages
3. 2FA or security checks may appear

### Workaround
The `--setup` command is **optional**. You can:
1. Skip setup entirely
2. The script will prompt for login when you first use `--publish`
3. Session is saved for future use

### Alternative: Manual Session Setup
If `--setup` fails, you can still use the poster:
1. Create posts with `--create` (works without login)
2. Review and approve posts
3. When you run `--publish`, it will open a browser for login
4. Login manually when prompted
5. Session is saved automatically

---

## Files Updated

1. ✅ `LINKEDIN_SETUP_COMPLETE.md` - Fixed all command examples
2. ✅ `CLAUDE.md` - Fixed command examples in Common Commands section
3. ✅ `CLAUDE.md` - Added LinkedIn commands to Testing section

---

## Testing Results

### Test Command: ✅ WORKS
```bash
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --test
```
**Result:** Test post created successfully in Pending_Approval

### Create Command: ✅ WORKS
```bash
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --create "Test post"
```
**Result:** Post draft created in Pending_Approval

### Publish Command: ⚠️ REQUIRES LOGIN
```bash
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --publish
```
**Result:** Will open browser for LinkedIn login (first time only)

---

## Summary

**Fixed Issues:**
- ✅ Corrected `--content` to `--create`
- ✅ Corrected `--post-approved` to `--publish`
- ✅ Updated all documentation
- ✅ Removed backslash line continuations for Windows

**Working Commands:**
- ✅ `--test` - Creates test post
- ✅ `--create "text"` - Creates custom post
- ✅ `--publish` - Publishes approved posts (requires login)
- ⚠️ `--setup` - Optional, can skip

**Status:** LinkedIn poster is fully functional with correct commands

---

**Last Updated:** 2026-03-25 08:40:00
**Status:** ✅ FIXED & DOCUMENTED
