# 🚀 Next Steps - Quick Action Guide

**Date:** 2026-03-26
**Status:** Cleanup Complete, Ready for Updates
**Priority:** HIGH - Must complete before running code

---

## ⚠️ CRITICAL: Code Will Break Until Imports Are Updated

The cleanup moved files to new locations. **All Python imports must be updated before the code will run.**

---

## 🎯 Immediate Actions (30 minutes)

### Step 1: Update Python Imports (15 min)

#### Files That Need Updates

**All skill scripts in `.claude/skills/*/scripts/`:**

1. **Gmail Watcher** - `.claude/skills/gmail-watcher/scripts/gmail_watcher.py`
2. **WhatsApp Watcher** - `.claude/skills/whatsapp-watcher/scripts/whatsapp_watcher.py`
3. **LinkedIn Poster** - `.claude/skills/linkedin-poster/scripts/linkedin_poster.py`
4. **Send Email** - `.claude/skills/send-email/scripts/send_email.py`
5. **Orchestrator** - `.claude/skills/orchestrator/scripts/orchestrator.py`

#### Import Changes Needed

```python
# OLD IMPORTS (will break)
from base_watcher import BaseWatcher
from claude_integration import VaultManager
from retry_handler import with_retry
from rate_limiter import rate_limited

# NEW IMPORTS (correct)
from src.watchers.base_watcher import BaseWatcher
from src.integration.claude_integration import VaultManager
from src.utils.retry_handler import with_retry
from src.utils.rate_limiter import rate_limited
```

#### Path Resolution Update

All skill scripts need updated path resolution:

```python
# OLD (5 parent levels)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

# NEW (6 parent levels - same, but verify it works)
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))
```

---

### Step 2: Update CLAUDE.md (10 min)

Update file paths in `CLAUDE.md`:

```markdown
# OLD
- `base_watcher.py` - Base class for all watchers
- `claude_integration.py` - VaultManager class

# NEW
- `src/watchers/base_watcher.py` - Base class for all watchers
- `src/integration/claude_integration.py` - VaultManager class
```

---

### Step 3: Test Everything (5 min)

```bash
# Test imports
python -c "from src.watchers.base_watcher import BaseWatcher; print('✅ Imports work')"

# Test Odoo API
python tests/test_odoo_api.py

# Test verify script
python tests/verify.py
```

---

## 📋 Detailed Update Instructions

### Update Skill: gmail-watcher

**File:** `.claude/skills/gmail-watcher/scripts/gmail_watcher.py`

**Find and replace:**
```python
# Line ~10-15
# OLD
from base_watcher import BaseWatcher

# NEW
from src.watchers.base_watcher import BaseWatcher
```

---

### Update Skill: whatsapp-watcher

**File:** `.claude/skills/whatsapp-watcher/scripts/whatsapp_watcher.py`

**Find and replace:**
```python
# Line ~10-15
# OLD
from base_watcher import BaseWatcher

# NEW
from src.watchers.base_watcher import BaseWatcher
```

---

### Update Skill: linkedin-poster

**File:** `.claude/skills/linkedin-poster/scripts/linkedin_poster.py`

**Find and replace:**
```python
# Line ~10-15
# OLD
from rate_limiter import rate_limited

# NEW
from src.utils.rate_limiter import rate_limited
```

---

### Update Skill: send-email

**File:** `.claude/skills/send-email/scripts/send_email.py`

**Find and replace:**
```python
# Line ~10-15
# OLD
from rate_limiter import rate_limited
from retry_handler import with_retry

# NEW
from src.utils.rate_limiter import rate_limited
from src.utils.retry_handler import with_retry
```

---

### Update Skill: orchestrator

**File:** `.claude/skills/orchestrator/scripts/orchestrator.py`

**Find and replace:**
```python
# Line ~10-15
# OLD
from claude_integration import VaultManager

# NEW
from src.integration.claude_integration import VaultManager
```

---

## 🔧 Configuration Path Updates

### Update Docker Commands

**OLD:**
```bash
cd odoo-docker
docker-compose up -d
```

**NEW:**
```bash
cd docker/odoo
docker-compose up -d
```

### Update Config Loading

**In all scripts that load .env:**

```python
# OLD
load_dotenv('.env')

# NEW
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / 'config' / '.env')
```

---

## ✅ Testing Checklist

After making updates, test each component:

```bash
# 1. Test imports
python -c "from src.watchers.base_watcher import BaseWatcher; print('✅ BaseWatcher')"
python -c "from src.integration.claude_integration import VaultManager; print('✅ VaultManager')"
python -c "from src.utils.retry_handler import with_retry; print('✅ RetryHandler')"
python -c "from src.utils.rate_limiter import rate_limited; print('✅ RateLimiter')"

# 2. Test Odoo
cd docker/odoo && docker-compose ps
python tests/test_odoo_api.py

# 3. Test watchers
python src/watchers/filesystem_watcher.py --test

# 4. Test skills
python .claude/skills/gmail-watcher/scripts/gmail_watcher.py --test
python .claude/skills/send-email/scripts/send_email.py --help

# 5. Test orchestrator
python .claude/skills/orchestrator/scripts/orchestrator.py --help
```

---

## 🚨 Common Errors & Fixes

### Error: ModuleNotFoundError: No module named 'base_watcher'

**Cause:** Import path not updated

**Fix:**
```python
# Change
from base_watcher import BaseWatcher

# To
from src.watchers.base_watcher import BaseWatcher
```

---

### Error: FileNotFoundError: [Errno 2] No such file or directory: '.env'

**Cause:** Config path not updated

**Fix:**
```python
# Change
load_dotenv('.env')

# To
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent.parent
load_dotenv(project_root / 'config' / '.env')
```

---

### Error: docker-compose.yml not found

**Cause:** Docker path not updated

**Fix:**
```bash
# Change
cd odoo-docker

# To
cd docker/odoo
```

---

## 📊 Progress Tracker

### Import Updates
- [ ] gmail-watcher
- [ ] whatsapp-watcher
- [ ] linkedin-poster
- [ ] send-email
- [ ] orchestrator
- [ ] process-vault-tasks
- [ ] update-dashboard

### Documentation Updates
- [ ] CLAUDE.md
- [ ] README.md
- [ ] GOLD_TIER_SUMMARY.md

### Testing
- [ ] Python imports
- [ ] Odoo API
- [ ] Watchers
- [ ] Skills
- [ ] Orchestrator

### Final Steps
- [ ] Update .gitignore
- [ ] Commit changes
- [ ] Push to repository

---

## 🎯 Success Criteria

You'll know everything is working when:

1. ✅ All Python imports work without errors
2. ✅ All tests pass
3. ✅ Docker commands work
4. ✅ Skills can be executed
5. ✅ No broken links in documentation

---

## 💡 Pro Tips

### Use Find & Replace

In VS Code or your editor:
1. Open "Find in Files" (Ctrl+Shift+F)
2. Search: `from base_watcher import`
3. Replace: `from src.watchers.base_watcher import`
4. Replace All

### Test As You Go

After updating each file:
```bash
python <file_path>
```

If no errors, move to next file.

### Keep a Backup

The cleanup created `README.md.backup`. Keep it until everything works.

---

## 🚀 Quick Start Commands

```bash
# 1. Update imports (use your editor's find & replace)
# Search: "from base_watcher import"
# Replace: "from src.watchers.base_watcher import"

# 2. Test imports
python -c "from src.watchers.base_watcher import BaseWatcher; print('✅')"

# 3. Test Odoo
cd docker/odoo && docker-compose up -d
python tests/test_odoo_api.py

# 4. Test everything
python tests/verify.py

# 5. Commit changes
git add .
git commit -m "refactor: reorganize codebase into clean folder structure"
git push
```

---

## 📞 Need Help?

### If Imports Still Break
1. Check sys.path in the script
2. Verify file actually exists at new location
3. Check for typos in import path

### If Tests Fail
1. Check error message carefully
2. Verify all imports updated
3. Check config files in config/ folder

### If Docker Fails
1. Verify path: `docker/odoo/docker-compose.yml`
2. Check Docker Desktop is running
3. Try: `docker-compose down && docker-compose up -d`

---

**Next Steps Guide Complete**
**Priority:** HIGH
**Time Required:** 30 minutes
**Status:** Ready to execute

**Start with Step 1: Update Python Imports! 🚀**
