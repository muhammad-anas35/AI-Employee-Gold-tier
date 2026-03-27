# Social Media Integration - Playwright Approach

**Date:** 2026-03-27
**Approach:** Using Playwright MCP (no API credentials needed)

---

## Why Playwright Instead of APIs?

### Advantages
- ✅ No developer accounts needed
- ✅ No API approval wait time
- ✅ Already configured in your system
- ✅ Works immediately
- ✅ Handles complex UI interactions
- ✅ Can post to any platform

### When to Use APIs Instead
- High volume posting (100+ posts/day)
- Need programmatic access to analytics
- Building public-facing app
- Need guaranteed uptime

---

## Implementation Plan

### Facebook/Instagram Posting (Playwright)

**Script:** `.claude/skills/facebook-poster/scripts/facebook_poster.py`

**Features:**
1. Login once, save session
2. Create post drafts in `/Pending_Approval`
3. Human reviews and approves
4. Publish from `/Approved` folder
5. Move to `/Done` with screenshot

**Workflow:**
```
User creates post → /Pending_Approval/POST_facebook_*.md
                              ↓
                    Human reviews & approves
                              ↓
                    Moves to /Approved/
                              ↓
                    Playwright opens browser
                              ↓
                    Posts to Facebook
                              ↓
                    Takes screenshot
                              ↓
                    Moves to /Done/ with proof
```

### Twitter Posting (Playwright)

**Script:** `.claude/skills/twitter-poster/scripts/twitter_poster.py`

**Features:**
1. Login once, save session
2. Create tweet drafts in `/Pending_Approval`
3. Human reviews and approves
4. Publish from `/Approved` folder
5. Support threads and images

---

## Setup Steps

### 1. Test Playwright MCP

```bash
# Check if Playwright is working
python -c "from playwright.sync_api import sync_playwright; print('OK')"
```

### 2. Create Facebook Poster Skill

```bash
mkdir -p .claude/skills/facebook-poster/scripts
```

### 3. Create Twitter Poster Skill

```bash
mkdir -p .claude/skills/twitter-poster/scripts
```

### 4. First-Time Setup

**For Facebook:**
1. Script opens browser
2. You log in manually
3. Session saved for future use
4. All future posts are automatic

**For Twitter:**
1. Script opens browser
2. You log in manually
3. Session saved for future use
4. All future posts are automatic

---

## Security

**Session Storage:**
- Cookies saved in: `.claude/skills/*/browser_data/`
- Encrypted and local only
- Never committed to Git

**Approval Workflow:**
- All posts require human approval
- Review content before publishing
- Can edit or reject posts

---

## Comparison: Playwright vs API

| Feature | Playwright | API |
|---------|-----------|-----|
| Setup Time | 5 minutes | 1-2 hours |
| Credentials | None | App ID, Secret, Tokens |
| Approval Wait | None | 0-24 hours |
| Speed | Slower (5-10s) | Fast (1-2s) |
| Reliability | 95% | 99% |
| Maintenance | Medium | Low |
| Cost | Free | Free (with limits) |

---

## Decision

**Start with Playwright now, add APIs later if needed.**

**Reasons:**
1. Faster to implement (today vs tomorrow)
2. No external dependencies
3. Already have Playwright configured
4. Can switch to APIs anytime

---

**Ready to implement?**

Type "continue" and I'll create the Facebook and Twitter poster skills using Playwright!
