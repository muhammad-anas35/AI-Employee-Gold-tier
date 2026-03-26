# 🎯 Gold Tier Quick Reference Card

**Last Updated:** 2026-03-26 11:42 UTC
**Status:** Ready for Implementation

---

## 📋 Today's Checklist

### Critical (Must Do First - 30 min)
- [ ] Read NEXT_STEPS.md
- [ ] Update Python imports in all skills
- [ ] Test imports work
- [ ] Update CLAUDE.md file paths

### Day 1 Tasks (2-3 hours)
- [ ] Install Docker Desktop
- [ ] Start Odoo containers
- [ ] Configure Odoo accounting
- [ ] Test Odoo API
- [ ] Create test invoice

---

## 🗂️ New File Locations

| What | Old Location | New Location |
|------|-------------|--------------|
| Watchers | `base_watcher.py` | `src/watchers/base_watcher.py` |
| Integration | `claude_integration.py` | `src/integration/claude_integration.py` |
| Utils | `retry_handler.py` | `src/utils/retry_handler.py` |
| Config | `mcp_config.json` | `config/mcp_config.json` |
| Docker | `odoo-docker/` | `docker/odoo/` |
| Tests | `test_odoo_api.py` | `tests/test_odoo_api.py` |
| Docs | Root directory | `docs/` folders |

---

## 🐍 Import Changes

```python
# OLD (will break)
from base_watcher import BaseWatcher
from claude_integration import VaultManager
from retry_handler import with_retry
from rate_limiter import rate_limited

# NEW (correct)
from src.watchers.base_watcher import BaseWatcher
from src.integration.claude_integration import VaultManager
from src.utils.retry_handler import with_retry
from src.utils.rate_limiter import rate_limited
```

---

## 🚀 Quick Commands

### Start Odoo
```bash
cd docker/odoo
docker-compose up -d
```

### Test Imports
```bash
python -c "from src.watchers.base_watcher import BaseWatcher; print('✅')"
```

### Test Odoo API
```bash
python tests/test_odoo_api.py
```

### Run Watchers
```bash
python src/watchers/filesystem_watcher.py
```

### Start Orchestrator
```bash
python .claude/skills/orchestrator/scripts/orchestrator.py
```

---

## 📚 Key Documents

| Need | Read This | Time |
|------|-----------|------|
| Quick overview | GOLD_TIER_SUMMARY.md | 5 min |
| What to do next | NEXT_STEPS.md | 5 min |
| What was cleaned | CLEANUP_FINAL_SUMMARY.md | 5 min |
| Complete status | PROJECT_STATUS_COMPLETE.md | 10 min |
| Setup guide | docs/guides/SETUP_INSTRUCTIONS.md | 10 min |
| Full spec | docs/planning/SPEC.md | 15 min |
| Implementation plan | docs/planning/GOLD_TIER_IMPLEMENTATION_PLAN.md | 20 min |

---

## 📊 Gold Tier Progress

**Current:** 5% (4/12 requirements partial)
**Target:** 100% by April 15, 2026
**Time Left:** 52 hours over 3 weeks

### This Week (30 hours)
- Day 1: Odoo setup
- Day 2: Social media accounts
- Day 3-4: Facebook/Instagram
- Day 5: Twitter
- Day 6-7: Testing

### Next Week (24 hours)
- Day 8-9: Business Audit
- Day 10-11: Ralph Wiggum
- Day 12: Cross-domain
- Day 13-14: Testing

### Final Week (22 hours)
- Day 15: Error recovery
- Day 16: Audit logging
- Day 17-18: Documentation
- Day 19: Testing
- Day 20: Demo video
- Day 21: Submission

---

## 🎯 Requirements Status

| # | Requirement | Status | Hours |
|---|------------|--------|-------|
| 1 | Silver requirements | ✅ DONE | 0 |
| 2 | Cross-domain | ⏳ 10% | 1.8 |
| 3 | Odoo accounting | ⏳ 20% | 8 |
| 4 | Facebook/Instagram | ❌ 0% | 8 |
| 5 | Twitter | ❌ 0% | 6 |
| 6 | MCP servers | ⏳ 40% | 2.4 |
| 7 | Business Audit | ❌ 0% | 8 |
| 8 | Error recovery | ⏳ 60% | 1.6 |
| 9 | Audit logging | ⏳ 50% | 1.5 |
| 10 | Ralph Wiggum | ❌ 0% | 6 |
| 11 | Documentation | ⏳ 20% | 2.4 |
| 12 | Agent Skills | ✅ DONE | 0 |

---

## 💰 Business Value

| Metric | Silver | Gold | Gain |
|--------|--------|------|------|
| Time Saved | 6 hrs/wk | 16 hrs/wk | +10 hrs |
| Annual Value | $20,600 | $61,600 | +$41,000 |
| ROI | 20x | 30x | +50% |
| Autonomy | 30% | 80% | +50% |

---

## 🚨 Common Errors

### ModuleNotFoundError
**Fix:** Update import paths (see above)

### FileNotFoundError: .env
**Fix:** Use `config/.env` path

### docker-compose.yml not found
**Fix:** Use `cd docker/odoo`

---

## 📞 Quick Help

### Stuck on imports?
→ Read NEXT_STEPS.md

### Need setup help?
→ Read docs/guides/SETUP_INSTRUCTIONS.md

### Lost in docs?
→ Read docs/README.md

### Want full plan?
→ Read docs/planning/SPEC.md

---

## ✅ Success Checklist

### Today
- [ ] Imports updated
- [ ] Docker installed
- [ ] Odoo running
- [ ] API tested

### This Week
- [ ] All integrations working
- [ ] Tests passing
- [ ] No critical bugs

### This Month
- [ ] All 12 requirements met
- [ ] Demo video recorded
- [ ] Gold tier submitted

---

## 🎯 Your Next Action

**RIGHT NOW:**
1. Open NEXT_STEPS.md
2. Update Python imports (15 min)
3. Test everything works
4. Install Docker Desktop
5. Start Day 1 tasks

---

**Quick Reference Card**
**Print this or keep it open!**
**Status:** Ready to implement
**Next:** NEXT_STEPS.md → Update imports

**Let's build Gold tier! 🚀**
