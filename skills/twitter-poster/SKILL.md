---
name: twitter-poster
description: Post tweets to Twitter/X using Playwright automation with approval workflow
---

# Twitter Poster Skill

Automatically post tweets to Twitter/X using browser automation.

## Features

- Browser-based posting (no API credentials needed)
- Approval workflow for all tweets
- Session persistence (login once)
- Screenshot proof of posting
- Support for text, images, and threads

## Usage

### Create a tweet

```bash
python .claude/skills/twitter-poster/scripts/twitter_poster.py --create "Your tweet content here"
```

### Publish approved tweets

```bash
python .claude/skills/twitter-poster/scripts/twitter_poster.py --publish
```

### Test setup

```bash
python .claude/skills/twitter-poster/scripts/twitter_poster.py --test
```

## Workflow

1. Create tweet → saved to `/Pending_Approval/TWEET_*.md`
2. Human reviews and approves → moves to `/Approved/`
3. Script publishes from `/Approved/` folder
4. Takes screenshot proof
5. Moves to `/Done/` with timestamp

## First-Time Setup

On first run, the script will:
1. Open Twitter in browser
2. Ask you to log in manually
3. Save session for future use
4. All future tweets are automatic

## Security

- Session cookies stored locally
- Never committed to Git
- All tweets require human approval
