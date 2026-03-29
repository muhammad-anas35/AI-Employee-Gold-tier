# 🎬 PRE-RECORDING SETUP GUIDE

**Date:** 2026-03-29
**Purpose:** Login to all platforms BEFORE recording demo

---

## 📋 STEP-BY-STEP LOGIN PROCESS

### Step 1: LinkedIn Login (5 min)

```bash
# Start LinkedIn poster in setup mode
python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --setup
```

**What will happen:**
1. Browser window opens
2. Navigate to LinkedIn login page
3. **YOU:** Login with your credentials
4. **YOU:** Complete any 2FA if needed
5. Browser session saved automatically
6. Close browser when done

**Status:** Session saved for future posts ✅

---

### Step 2: Twitter/X Login (5 min)

```bash
# Start Twitter poster in setup mode
python .claude/skills/twitter-poster/scripts/twitter_poster.py --setup
```

**What will happen:**
1. Browser window opens
2. Navigate to Twitter login page
3. **YOU:** Login with your credentials
4. **YOU:** Complete any 2FA if needed
5. Browser session saved automatically
6. Close browser when done

**Status:** Session saved for future tweets ✅

---

### Step 3: Facebook Login (5 min)

```bash
# Start Facebook poster in setup mode
python .claude/skills/facebook-poster/scripts/facebook_poster.py --setup
```

**What will happen:**
1. Browser window opens
2. Navigate to Facebook login page
3. **YOU:** Login with your credentials
4. **YOU:** Complete any 2FA if needed
5. Browser session saved automatically
6. Close browser when done

**Status:** Session saved for future posts ✅

---

### Step 4: Verify Gmail (Already Done) ✅

**Gmail is already configured:**
- credentials.json ✅
- token.json ✅
- No additional login needed ✅

---

## ✅ AFTER ALL LOGINS COMPLETE

**You will have:**
1. ✅ LinkedIn session active
2. ✅ Twitter session active
3. ✅ Facebook session active
4. ✅ Gmail already configured

**Then you can:**
1. Start your recording setup
2. Tell me when ready
3. I'll execute ALL actions LIVE:
   - Send REAL email
   - Post REAL LinkedIn post
   - Post REAL Twitter tweet
   - Post REAL Facebook post

---

## 🎥 RECORDING SETUP CHECKLIST

Before you tell me to execute:

- [ ] Screen recording software ready (OBS Studio recommended)
- [ ] Microphone tested
- [ ] All platforms logged in
- [ ] Browser sessions saved
- [ ] poster.jpeg file ready
- [ ] Vault folders visible
- [ ] Ready to record

---

## 🎬 EXECUTION SEQUENCE (When You're Ready)

**When you say "execute":**

1. **Send Email** (30 sec)
   ```bash
   python .claude/skills/send-email/scripts/send_email.py --send-approved
   ```
   - Sends email to alibahi353570@gmail.com
   - Shows success message
   - Moves to Done folder

2. **Post to LinkedIn** (1 min)
   ```bash
   python .claude/skills/linkedin-poster/scripts/linkedin_poster.py --publish
   ```
   - Opens browser
   - Posts with poster.jpeg
   - Takes screenshot
   - Saves to Done folder

3. **Post to Twitter** (1 min)
   ```bash
   python .claude/skills/twitter-poster/scripts/twitter_poster.py --publish
   ```
   - Opens browser
   - Posts tweet with poster.jpeg
   - Takes screenshot
   - Saves to Done folder

4. **Post to Facebook** (1 min)
   ```bash
   python .claude/skills/facebook-poster/scripts/facebook_poster.py --publish
   ```
   - Opens browser
   - Posts with poster.jpeg
   - Takes screenshot
   - Saves to Done folder

**Total Time:** ~4 minutes for all executions

---

## 📊 WHAT YOU'LL SEE IN VIDEO

1. **Before Execution:**
   - 4 items in Approved folder
   - All ready to go

2. **During Execution:**
   - Email sending confirmation
   - LinkedIn browser posting
   - Twitter browser posting
   - Facebook browser posting
   - Real-time progress

3. **After Execution:**
   - 4 items moved to Done folder
   - Screenshots saved
   - Audit logs updated
   - Dashboard updated

---

## 🎯 NEXT STEPS

**RIGHT NOW:**
1. Login to LinkedIn (5 min)
2. Login to Twitter (5 min)
3. Login to Facebook (5 min)
4. Setup your recording software
5. Tell me when ready

**THEN:**
- I'll execute everything LIVE
- You record the whole process
- Perfect demo video! 🎬

---

## ⚠️ IMPORTANT NOTES

1. **Browser Sessions:** Will stay logged in for future use
2. **Gmail:** Already configured, no login needed
3. **Recording:** Start recording BEFORE telling me to execute
4. **Timing:** Each platform takes ~1 minute
5. **Screenshots:** Automatically saved as proof

---

**Ready to start logging in to platforms?**

**Just run the setup commands above for each platform!** 👍

---

**Generated:** 2026-03-29 19:12 UTC
**Status:** Waiting for platform logins
**Next:** Tell me when recording setup is done
